import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class DI(Chain):
    def __init__(self, x=0.5, y=0.5, cx = 0.5, cy = 0.5):
        self.x = x
        self.y = y
        self.cx = cx
        self.cy = cy

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        self.interruptible = True
        controller.release_button(Button.BUTTON_L)
        controller.release_button(Button.BUTTON_Y)
        controller.tilt_analog(Button.BUTTON_MAIN, self.x, self.y)
        controller.tilt_analog(Button.BUTTON_C, self.cx, self.cy)
