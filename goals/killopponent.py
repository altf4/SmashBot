from util import enums
from goals import goal
import globals

class KillOpponent(goal.Goal):

    def pickstrategy(self):
        game_state = globals.gamestate
        smashbot_state = globals.smashbot_state
        controller = globals.controller

        #Are we at the character select screen?
        if game_state.menu_state == enums.Menu.CHARACTER_SELECT:
            pass
