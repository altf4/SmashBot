import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

# Dropdownshine
class Dropdownshine(Chain):
    # To be checked once at the start of the chain
    def inrange(smashbot_state, opponent_state, framedata):
        # We must be edge hanging
        if smashbot_state.action != Action.EDGE_HANGING:
            return False

        # They must be below us
        if opponent_state.y > smashbot_state.y:
            return False

        # If opponent can grab the edge, don't go
        #   -25 is really conservative. 15 is more likely
        if -25 < opponent_state.y and opponent_state.speed_y_self < 0:
            return False

        # Opponent must be moving slowly horizontally
        if abs(opponent_state.speed_air_x_self) > 1.5:
            return False

        # Fastfall speed is 3.4, how long will it take to get to the opponent vertically?
        frames_y = abs(opponent_state.y - smashbot_state.y) // 3.4

        # Horizontal speed is 0.819625854, how long will it take to get to the opponent horizontally?
        #   But we won't be able to use the full horizontal speed. So half it
        frames_x = abs(opponent_state.x - smashbot_state.x) // (0.819625854 / 2)

        # If opponent is in a FireFox, we have to get there before they take off
        framesleft = framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame
        latefirefox = opponent_state.character in [Character.FOX, Character.FALCO] and \
            opponent_state.action == Action.SWORD_DANCE_3_LOW and (smashbot_state.invulnerability_left < framesleft)

        # Vertical frames are set in stone, so we need to make sure that the horizontal need is smaller
        # We also need to have enough invulnerability
        if (frames_x <= frames_y) and (smashbot_state.invulnerability_left >= frames_y) and not latefirefox:
            return True

        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        # Do an emergency shine if we run out of invulnerability, then end the chain
        if smashbot_state.invulnerability_left == 0 and smashbot_state.action != Action.EDGE_HANGING:
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
            controller.tilt_analog(melee.Button.BUTTON_C, int(not smashbot_state.facing), 0.5)
            return

        # Do the shine
        if gamestate.distance < 11.8:
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
