import melee
from melee.enums import Button
from Chains.chain import Chain

# Struggle out of a grab
class Struggle(Chain):
    def step(self):
        # Just naively press and release every button every other frame
        controller = self.controller

        # Press every button
        if self.gamestate.frame % 2:
            controller.press_button(Button.BUTTON_A);
            controller.press_button(Button.BUTTON_B);
            controller.press_button(Button.BUTTON_X);
            controller.press_button(Button.BUTTON_Y);
            controller.press_button(Button.BUTTON_L);
            controller.press_button(Button.BUTTON_R);
            controller.press_button(Button.BUTTON_Z);
        # Release every button
        else:
            controller.release_button(Button.BUTTON_A);
            controller.release_button(Button.BUTTON_B);
            controller.release_button(Button.BUTTON_X);
            controller.release_button(Button.BUTTON_Y);
            controller.release_button(Button.BUTTON_L);
            controller.release_button(Button.BUTTON_R);
            controller.release_button(Button.BUTTON_Z);

        if (self.gamestate.frame % 4) == 0:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            controller.tilt_analog(Button.BUTTON_C, .5, 0)
        if (self.gamestate.frame % 4) == 1:
            controller.tilt_analog(Button.BUTTON_MAIN, 1, .5)
            controller.tilt_analog(Button.BUTTON_C, 1, .5)
        if (self.gamestate.frame % 4) == 2:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 1)
            controller.tilt_analog(Button.BUTTON_C, .5, 1)
        if (self.gamestate.frame % 4) == 3:
            controller.tilt_analog(Button.BUTTON_MAIN, 0, .5)
            controller.tilt_analog(Button.BUTTON_C, 0, .5)
