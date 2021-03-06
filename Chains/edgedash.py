import melee
from melee.enums import Action, Button
from Chains.chain import Chain

# Edgedash
class Edgedash(Chain):
    def __init__(self, refresh):
        self.hasstalled = False
        self.letgoframe = 0
        self.refresh = refresh

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        # If we just grabbed the edge, just wait
        if smashbot_state.action == Action.EDGE_CATCHING:
            self.interruptible = True
            controller.empty_input()
            return

        if smashbot_state.action == Action.SWORD_DANCE_3_LOW:
            self.hasstalled = True
            self.interruptible = False
            controller.empty_input()
            return

        # Do a firefox stall
        if not self.hasstalled and self.refresh:
            # If we are able to let go of the edge, do it
            if smashbot_state.action == Action.EDGE_HANGING:
                # If we already pressed back last frame, let go
                if controller.prev.c_stick != (0.5, 0.5):
                    self.interruptible = False
                    controller.empty_input()
                    return
                x = 1
                if smashbot_state.position.x < 0:
                    x = 0
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_C, x, 0.5)
                return

            # Once we're falling, UP-B
            if smashbot_state.action == Action.FALLING:
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
                controller.press_button(Button.BUTTON_B)
                return

            self.interruptible = False
            controller.empty_input()
            return

        # If we are able to let go of the edge, do it
        if smashbot_state.action == Action.EDGE_HANGING:
            # If we already pressed back last frame, let go
            if controller.prev.c_stick != (0.5, 0.5):
                controller.empty_input()
                return
            x = 1
            if smashbot_state.position.x < 0:
                x = 0
            self.interruptible = False
            self.letgoframe = gamestate.frame
            controller.tilt_analog(Button.BUTTON_C, x, 0.5)
            return

        # Once we're falling, jump
        if smashbot_state.action == Action.FALLING:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0.5)
            controller.press_button(Button.BUTTON_Y)
            return

        # Jumping, stay in the chain and DI in
        if smashbot_state.action == Action.JUMPING_ARIAL_FORWARD:
            if smashbot_state.position.y + smashbot_state.ecb.bottom.y > 0:
                x = 0
                if smashbot_state.position.x < 0:
                    x = 1
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, x, 0.2)
                controller.press_button(Button.BUTTON_L)
                return
            else:
                x = 0
                if smashbot_state.position.x < 0:
                    x = 1
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, x, 0.5)
                return

        self.interruptible = True
        controller.empty_input()
