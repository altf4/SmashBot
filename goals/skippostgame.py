from util import enums
from goals import goal
import globals

class SkipPostgame(goal.Goal):

    #NOTE: We just go ahead and press the buttons here rather than deferring to
    #   a strategy since selecting a character is simple, and it would just muddy
    #   the logic of combat, which is more important anyway
    def pickstrategy(self):
        game_state = globals.gamestate
        smashbot_state = globals.smashbot_state
        controller = globals.controller

        #Was the start button pressed last frame?
        if controller.prev.button[enums.Button.BUTTON_START] == False:
            controller.press_button(enums.Button.BUTTON_START)
        else:
            controller.release_button(enums.Button.BUTTON_START)
