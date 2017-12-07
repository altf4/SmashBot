import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class DI(Chain):
    def __init__(self, x=0.5, y=0.5):
        self.x = x
        self.y = y

    def step(self):
        controller = self.controller
        self.interruptible = True
        controller.release_button(Button.BUTTON_L)
        controller.tilt_analog(Button.BUTTON_MAIN, self.x, self.y)
