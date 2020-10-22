import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Airdodge(Chain):
    def __init__(self, x=0.5, y=0.5):
        self.x = x
        self.y = y

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        self.interruptible = True
        controller.press_button(Button.BUTTON_L)
        controller.tilt_analog(Button.BUTTON_MAIN, self.x, self.y)
