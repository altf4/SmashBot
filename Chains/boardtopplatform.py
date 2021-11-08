import melee
import random
from Chains.chain import Chain
from melee.enums import Action, Button, Stage

class BoardTopPlatform(Chain):
    """The general strategy here is to do a dashing jump from a side platform towards the center platform. Waveland down to it."""
    def __init__(self):
        self.interruptible = True

    def step(self, gamestate, smashbot_state, opponent_state):
        platform_center = 0
        platform_height = 0

        plat_position = melee.top_platform_position(gamestate.stage)
        if plat_position:
            platform_center = (plat_position[1] + plat_position[2]) / 2
            platform_height = plat_position[0]
        else:
            self.interruptible = True
            self.controller.empty_input()
            return

        on_side_platform = smashbot_state.on_ground and smashbot_state.position.y > 5
        above_top_platform = (not smashbot_state.on_ground) and (smashbot_state.position.y + smashbot_state.ecb.bottom.y > platform_height) and \
            plat_position[1] < smashbot_state.position.x < plat_position[2]

        if smashbot_state.on_ground and smashbot_state.action != Action.KNEE_BEND:
            self.interruptible = True

        if on_side_platform:
            self.interruptible = True
            self.controller.empty_input()
            return

        # If we're crouching, release holding Y
        if smashbot_state.action == Action.KNEE_BEND:
            self.controller.release_button(melee.Button.BUTTON_Y)
            self.interruptible = False
            return

        # Don't jump into Peach's dsmash or SH early dair spam
        dsmashactive = opponent_state.action == Action.DOWNSMASH and opponent_state.action_frame <= 22
        if opponent_state.action == Action.DAIR or dsmashactive:
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        jump_frame = 30
        if gamestate.stage == Stage.BATTLEFIELD:
            jump_frame = 14
        if gamestate.stage == Stage.DREAMLAND:
            jump_frame = 16
        if gamestate.stage == Stage.YOSHIS_STORY:
            jump_frame = 21

        # Double jump
        if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
            if smashbot_state.action_frame == jump_frame:
                if random.randint(0, 3) == 0:
                    self.controller.press_button(melee.Button.BUTTON_Y)
                    self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0.5)
                    self.interruptible = False
                    return
                else:
                    self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                    return

        # Drift into opponent
        if smashbot_state.action in [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD, Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
            self.interruptible = False
            self.controller.release_button(melee.Button.BUTTON_Y)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < opponent_state.position.x), 0.5)
            return

        # Dash at the position of the opponent
        if smashbot_state.on_ground and smashbot_state.position.y < 10:
            self.interruptible = True
            pivotpoint = opponent_state.position.x
            pivotpoint = min(plat_position[2]-7, pivotpoint)
            pivotpoint = max(plat_position[1]+7, pivotpoint)

            if abs(smashbot_state.position.x - pivotpoint) < 5 and smashbot_state.action == Action.TURNING:
                self.interruptible = False
                self.controller.press_button(melee.Button.BUTTON_Y)
                return

            if smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
                return
            if smashbot_state.action == Action.DASHING and smashbot_state.action_frame >= 11:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
                return
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < pivotpoint), 0.5)
            return

        self.controller.empty_input()
