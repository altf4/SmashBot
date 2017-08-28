import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class SHFFL_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2
    BACK = 3
    NEUTRAL = 4

class Shffl(Chain):
    def step(self, direction=SHFFL_DIRECTION.DOWN):
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        controller = globals.controller

        # If we're in knee bend, let go of jump. But move toward opponent
        if smashbot_state.action == Action.KNEE_BEND:
            self.interruptible = False
            controller.release_button(Button.BUTTON_Y);
            jumpdirection = 1
            if opponent_state.x < smashbot_state.x:
                jumpdirection = -1
            controller.tilt_analog(Button.BUTTON_MAIN, jumpdirection, .5)
            return

        # If we're on the ground, but NOT in knee bend, then jump
        if smashbot_state.on_ground:
            if controller.prev.button[Button.BUTTON_Y]:
                self.interruptible = True
                controller.empty_input()
            else:
                self.interruptible = False
                controller.press_button(Button.BUTTON_Y)
            return

        # If we're falling, then press down hard to do a fast fall, and press L to L cancel
        if smashbot_state.speed_y_self < 0:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            # Only do the L cancel near the end of the animation
            if smashbot_state.action_frame >= 12:
                controller.press_button(Button.BUTTON_L)
            return

        # Once we're airborn, do an attack
        if not globals.framedata.isattack(smashbot_state.character, smashbot_state.action):
            # If the C stick wasn't set to middle, then
            if controller.prev.c_stick != (.5, .5):
                controller.tilt_analog(Button.BUTTON_C, .5, .5)
                return

            if direction == SHFFL_DIRECTION.UP:
                controller.tilt_analog(Button.BUTTON_C, .5, 1)
            if direction == SHFFL_DIRECTION.DOWN:
                controller.tilt_analog(Button.BUTTON_C, .5, 0)
            if direction == SHFFL_DIRECTION.FORWARD:
                controller.tilt_analog(Button.BUTTON_C, int(smashbot_state.facing), .5)
            if direction == SHFFL_DIRECTION.BACK:
                controller.tilt_analog(Button.BUTTON_C, int(not smashbot_state.facing), .5)
            if direction == SHFFL_DIRECTION.NEUTRAL:
                controller.press_button(Button.BUTTON_A)
                controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)
            return
        elif smashbot_state.speed_y_self > 0:
            controller.empty_input()
            return

        self.interruptible = True
        controller.empty_input()
