import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

class Run(Chain):
    def __init__(self, rundirection):
        self.rundirection = rundirection

    def step(self):
        controller = globals.controller
        # Run in the specified direction
        x = 0
        if self.rundirection:
            x = 1
        controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
        self.interruptible = True
