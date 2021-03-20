import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class TILT_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2

class Tilt(Chain):
    def __init__(self, direction=TILT_DIRECTION.UP):
        """NOTE: Don't call this from a dashing state. You need to pivot into it, but then the attack goes the wrong way.
            It's not like shine, where it hits all around. And it'd be too complex here to figure out which way is the right way."""
        self.direction = direction

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        if smashbot_state.action == Action.LANDING_SPECIAL:
            self.interruptible = True
            controller.empty_input()
            return

        # Do the tilt, unless we were already pressing A
        if controller.prev.button[Button.BUTTON_A]:
            controller.empty_input()
            return

        controller.press_button(Button.BUTTON_A)
        if self.direction == TILT_DIRECTION.UP:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.65)
        elif self.direction == TILT_DIRECTION.DOWN:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.35)
        elif self.direction == TILT_DIRECTION.FORWARD:
            x = 0.35
            if smashbot_state.facing:
                x = 0.65
            controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
