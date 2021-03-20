import melee
import random
from Chains.chain import Chain
from melee.enums import Action, Button

class BoardTopPlatform(Chain):
    """The general strategy here is to do a dashing jump from a side platform towards the center platform. Waveland down to it."""
    def __init__(self):
        self.interruptible = True

    def step(self, gamestate, smashbot_state, opponent_state):
        platform_center = 0
        platform_height = 0

        position = melee.top_platform_position(gamestate.stage)
        if position:
            platform_center = (position[1] + position[2]) / 2
            platform_height = position[0]

        on_side_platform = smashbot_state.on_ground and smashbot_state.position.y > 5
        above_top_platform = (not smashbot_state.on_ground) and (smashbot_state.position.y + smashbot_state.ecb.bottom.y > platform_height) and \
            position[1] < smashbot_state.position.x < position[2]

        if smashbot_state.on_ground and smashbot_state.action != Action.KNEE_BEND:
            self.interruptible = True

        # Stage 1, get to the inside edge of the side platform
        #   Are we in position to jump? We want to be dashing inwards on a side plat
        if on_side_platform:
            # Get the x coord of the inner edge of the plat
            right_edge = (melee.side_platform_position(True, gamestate.stage))[2]
            if right_edge - abs(smashbot_state.position.x) < 8:
                if smashbot_state.action in [Action.DASHING, Action.RUNNING] and (smashbot_state.facing == (smashbot_state.position.x < 0)):
                    self.interruptible = False
                    self.controller.press_button(melee.Button.BUTTON_Y)
                    return
                else:
                    # Dash inwards
                    self.interruptible = False
                    self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0.5)
                    return
            else:
                # Dash inwards
                self.interruptible = False
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0.5)
                return

        # If we're crouching, keep holding Y
        if smashbot_state.action == Action.KNEE_BEND:
            self.controller.press_button(melee.Button.BUTTON_Y)
            self.interruptible = False
            return

        # Jump when falling
        if smashbot_state.action == Action.FALLING and smashbot_state.jumps_left > 0 and smashbot_state.action_frame > 6:
            self.interruptible = False
            self.controller.press_button(melee.Button.BUTTON_Y)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0.5)
            return

        # Jump out of shine
        if smashbot_state.action in [Action.DOWN_B_AIR]:
            self.controller.press_button(melee.Button.BUTTON_Y)
            return

        # Can we shine our opponent right now, while we're in the air?
        foxshinerange = 11.8
        shineable = smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]
        if shineable and gamestate.distance < foxshinerange:
            self.controller.press_button(melee.Button.BUTTON_B)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Waveland down
        aerials = [Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR, Action.DAIR]
        if above_top_platform and smashbot_state.action not in aerials:
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            # If opponent is in front of us, waveland towards them
            if smashbot_state.facing == (smashbot_state.position.x < opponent_state.position.x):
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < opponent_state.position.x), 0.2)
            else:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Don't jump into Peach's dsmash or SH early dair spam
        dsmashactive = opponent_state.action == Action.DOWNSMASH and opponent_state.action_frame <= 22
        if shineable and (opponent_state.action == Action.DAIR or dsmashactive):
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Hold inwards while we're jumping
        if shineable:
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0.5)
            return

        # Last resort, just dash at the center of the platform
        if smashbot_state.on_ground:
            self.interruptible = True
            #If we're starting the turn around animation, keep pressing that way or
            #   else we'll get stuck in the slow turnaround
            if smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
                return

            #Dash back, since we're about to start running
            if smashbot_state.action == Action.DASHING and smashbot_state.action_frame >= 11:
                    self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
                    return
            if smashbot_state.position.x > platform_center + 2:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
                return
            if smashbot_state.position.x < platform_center - 2:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                return
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.facing), .5)
            return
        # Mash analog L presses to L-cancel if Smashbot is throwing out an aerial
        elif not smashbot_state.on_ground and smashbot_state.action in aerials:
            self.interruptible = False
            if gamestate.frame % 2 == 0:
                self.controller.press_shoulder(Button.BUTTON_L, 1)
            else:
                self.controller.press_shoulder(Button.BUTTON_L, 0)
            return
        else:
            self.controller.empty_input()
