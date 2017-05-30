import melee
import globals
import Chains
from Tactics.tactic import Tactic

class Approach(Tactic):
    def step(self):
        # TODO: For now, just dash dance at our opponent
        # Let's make this a bit more sophisticated perhaps
        self.chain = None
        self.pickchain(Chains.DashDance, [globals.opponent_state.x])
