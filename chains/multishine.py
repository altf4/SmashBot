from chains import chain
from util import enums
import globals

class MultiShine(chain.Chain):

    def pressbuttons(self):
        game_state = globals.gamestate
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        controller = globals.controller

        #If standing, shine, become uninteruptible
        if smashbot_state.action == enums.Action.STANDING:
            controller.press_button(enums.Button.BUTTON_B)
            controller.tilt_analog(enums.Button.BUTTON_MAIN, .5, 0)
            self.interruptible = False
            return

        #Shine on frame 3 of knee bend, else nothing
        if smashbot_state.action == enums.Action.KNEE_BEND:
            if smashbot_state.action_frame == 2:
                controller.press_button(enums.Button.BUTTON_B)
                controller.tilt_analog(enums.Button.BUTTON_MAIN, .5, 0)
                self.interruptible = False
                return
            else:
                controller.empty_input()
                return

        isInShineStart = (smashbot_state.action == enums.Action.DOWN_B_STUN or
                smashbot_state.action == enums.Action.DOWN_B_GROUND_START)

        #Jump out of shine
        if isInShineStart and smashbot_state.action_frame >= 4 and smashbot_state.on_ground:
            controller.press_button(enums.Button.BUTTON_Y)
            return

        if smashbot_state.action == enums.Action.DOWN_B_GROUND:
            controller.press_button(enums.Button.BUTTON_Y)
            return

        controller.empty_input()
