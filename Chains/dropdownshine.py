import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# Dropdownshine
class Dropdownshine(Chain):
    # To be checked once at the start of the chain
    def inrange():
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # We must be edge hanging
        if smashbot_state.action != Action.EDGE_HANGING:
            return False

        # They must be below us
        if opponent_state.y > smashbot_state.y:
            return False

        # Fastfall speed is 3.4, how long will it take to get to the opponent vertically?
        frames_y = abs(opponent_state.y - smashbot_state.y) // 3.4

        # Horizontal speed is 0.819625854, how long will it take to get to the opponent horizontally?
        #   But we won't be able to use the full horizontal speed. So half it
        frames_x = abs(opponent_state.x - smashbot_state.x) // (0.819625854 / 2)

        # Vertical frames are set in stone, so we need to make sure that the horizontal need is smaller
        # We also need to have enough invulnerability
        if (frames_x <= frames_y) and (smashbot_state.invulnerability_left >= frames_y):
            return True

        return False

    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # Do an emergency shine if we run out of invulnerability, then end the chain
        if smashbot_state.invulnerability_left == 0:
            self.interruptible = True
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            controller.press_button(Button.BUTTON_B)
            return

        # End the chain if we are in shine
        if smashbot_state.action == Action.DOWN_B_STUN:
            self.interruptible = True
            controller.press_button(Button.BUTTON_Y)
            return

        # Drop down with a fastfall
        if smashbot_state.action == Action.EDGE_HANGING:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # Do the shine
        if globals.gamestate.distance < 11.8:
            self.interruptible = True
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            controller.press_button(Button.BUTTON_B)
            return

        # Fastfall if we aren't already
        # Fastfall speed is 3.4, but we need a little wiggle room
        if smashbot_state.action == Action.FALLING and smashbot_state.speed_y_self > -3.35:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            return

        # DI in toward the opponent
        self.interruptible = False
        x = 0
        if smashbot_state.x < opponent_state.x:
            x = 1
        controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
