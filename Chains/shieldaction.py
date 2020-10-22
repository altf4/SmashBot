import melee
import Tactics
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class SHIELD_ACTION(Enum):
    PSSHINE = 0
    PSUTILT = 1
    PSDTILT = 2
    PSJAB = 3

class ShieldAction(Chain):
    def __init__(self, action=SHIELD_ACTION.PSSHINE):
        self.action = action

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        self.interruptible = True

        # Let go of A if we were already pressing A
        if controller.prev.button[Button.BUTTON_A]:
            controller.empty_input()
            return

        # Let go of B if we were already pressing B
        if controller.prev.button[Button.BUTTON_B]:
            controller.empty_input()
            return

        # Consider adding redundancy to check for SHIELD_RELEASE, but this just has button inputs atm
        if self.action == SHIELD_ACTION.PSSHINE:
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, .3)
            return
        if self.action == SHIELD_ACTION.PSUTILT:
            controller.press_button(Button.BUTTON_A)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.7)
            return
        elif self.action == SHIELD_ACTION.PSDTILT:
            controller.press_button(Button.BUTTON_A)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.3)
            return
        elif self.action == SHIELD_ACTION.PSJAB:
            controller.press_button(Button.BUTTON_A)
            return
