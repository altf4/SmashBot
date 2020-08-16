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

        under_platform = abs(smashbot_state.x - platform_center) < 10

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
        if smashbot_state.ecb_bottom[1] + smashbot_state.y > platform_height:
            self.interruptible = True
            self.controller.press_button(melee.Button.BUTTON_L)
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
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
            if smashbot_state.x > platform_center + 2:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
                return
            if smashbot_state.x < platform_center - 2:
                self.controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
                return
            self.controller.tilt_analog(melee.Button.BUTTON_MAIN, int(smashbot_state.facing), .5)
            return
        else:
            self.controller.empty_input()
