from util import enums
from goals import goal
from strategies import sandbag, bait
import globals

class KillOpponent(goal.Goal):

    def pickstrategy(self):
        game_state = globals.gamestate
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        controller = globals.controller

        #If enemy is invulnerable, but not in one of a couple known states, then sandbag
        #TODO: This should be for any roll
        sandbagState = (opponent_state.invulnerable and
            opponent_state.action != EDGE_GETUP_SLOW and
            opponent_state.action != EDGE_GETUP_QUICK and
            opponent_state.action != EDGE_ROLL_SLOW and
            opponent_state.action != EDGE_ROLL_QUICK)

        if sandbagState:
            self.createstrategy(sandbag.SandBag)
            self.strategy.picktactic()
            return
        else:
            self.createstrategy(bait.Bait)
            self.strategy.picktactic()
            return
