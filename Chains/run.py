import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

class Run(Chain):
    def step(self, rundirection):
        # Run in the specified direction
        controller.tilt_analog(Button.BUTTON_MAIN, int(rundirection), .5)
        self.interruptible = True
