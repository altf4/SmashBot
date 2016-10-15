from chains import chain
from util import enums
import globals

class SkipPostgame(chain.Chain):

    def pressbuttons(self):
        game_state = globals.gamestate
        smashbot_state = globals.smashbot_state
        controller = globals.controller

        #Was the start button pressed last frame?
        if controller.prev.button[enums.Button.BUTTON_START] == False:
            controller.press_button(enums.Button.BUTTON_START)
        else:
            controller.release_button(enums.Button.BUTTON_START)
