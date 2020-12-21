import melee
import random
from Chains.chain import Chain
from melee.enums import Action, Button

class BoardSidePlatform(Chain):
    def __init__(self, right_platform):
        self.right_platform = right_platform
        self.interruptible = True

    def step(self, gamestate, smashbot_state, opponent_state):

        platform_center = 0
        platform_height = 0

        position = melee.side_platform_position(self.right_platform, gamestate)
        if position:
            platform_center = (position[1] + position[2]) / 2
            platform_height = position[0]

        under_platform = abs(smashbot_state.position.x - platform_center) < 10

        if smashbot_state.on_ground:
            self.interruptible = True

        # Are we in position to jump?
        if under_platform and smashbot_state.action == Action.TURNING:
            self.interruptible = False
            self.controller.press_button(melee.Button.BUTTON_Y)
            return

        # If we're crouching, keep holding Y
        if smashbot_state.action == Action.KNEE_BEND:
            self.controller.press_button(melee.Button.BUTTON_Y)
            self.interruptible = False
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
        if smashbot_state.ecb.bottom.y + smashbot_state.position.y > platform_height and smashbot_state.action not in aerials:
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Don't jump into Peach's dsmash or SH early dair spam
        dsmashactive = opponent_state.action == Action.DOWNSMASH and opponent_state.action_frame <= 22
        if shineable and (opponent_state.action == Action.DAIR or dsmashactive):
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # If we see the opponent jump, they cannot protect themselves from uair.
        # Does not look for KNEE_BEND because Smashbot needs to discern between SH and FH
        y_afternineframes = opponent_state.position.y
        gravity = self.framedata.characterdata[opponent_state.character]["Gravity"]
        y_speed = opponent_state.speed_y_self
        for i in range(1,10):
            y_afternineframes += y_speed
            y_speed -= gravity


        aerialsminusdair = [Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR]
        if shineable and (opponent_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] or opponent_state.action in aerialsminusdair) and y_afternineframes < 50:
            self.controller.press_button(melee.Button.BUTTON_A)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
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
