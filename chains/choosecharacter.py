from util import enums
from chains import chain
import globals

class ChooseCharacter(chain.Chain):

    def pressbuttons(self):
        smashbot_state = globals.smashbot_state
        controller = globals.controller

        #We want to get to a state where the cursor is NOT over Fox, but he's selected
        # Thus ensuring the token is on Fox
        isOverFox = (smashbot_state.cursor_x > -27 and
            smashbot_state.cursor_x < -20 and
            smashbot_state.cursor_y > 8 and
            smashbot_state.cursor_y < 15)

        #Don't hold down on B, since we'll quit the menu if we do
        if controller.prev.button[enums.Button.BUTTON_B] == True:
            controller.release_button(enums.Button.BUTTON_B)
            return

        #If we're in the fox area, select Fox
        if isOverFox:
            #If we're over fox, but fox isn't selected, then the coin must be somewhere else.
            #   Press B to reclaim the coin
            controller.tilt_analog(enums.Button.BUTTON_MAIN, .5, .5)
            if smashbot_state.character != enums.Character.FOX:
                controller.press_button(enums.Button.BUTTON_B)
                return
            #Press A to select our character
            else:
                if controller.prev.button[enums.Button.BUTTON_A] == False:
                    controller.press_button(enums.Button.BUTTON_A)
                    return
                else:
                    controller.release_button(enums.Button.BUTTON_A)
                    return

        #If fox is selected, and we're out of the fox area, then we're good. Do nothing
        if (isOverFox == False) and (smashbot_state.character == enums.Character.FOX):
            controller.empty_input()
            return

        #If fox is NOT selected and we're out of the fox area, then move in
        if (isOverFox == False) and (smashbot_state.character != enums.Character.FOX):
            controller.release_button(enums.Button.BUTTON_A)
            #Move up if we're too low
            if smashbot_state.cursor_y < 8:
                controller.tilt_analog(enums.Button.BUTTON_MAIN, .5, 1)
                return
            #Move downn if we're too high
            if smashbot_state.cursor_y > 15:
                controller.tilt_analog(enums.Button.BUTTON_MAIN, .5, 0)
                return
            #Move right if we're too left
            if smashbot_state.cursor_x < -27:
                controller.tilt_analog(enums.Button.BUTTON_MAIN, 1, .5)
                return
            #Move left if we're too right
            if smashbot_state.cursor_x > -20:
                controller.tilt_analog(enums.Button.BUTTON_MAIN, 0, .5)
                return

            controller.empty_input()
