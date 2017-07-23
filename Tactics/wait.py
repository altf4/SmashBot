import melee
import Chains
from Tactics.tactic import Tactic

class Wait(Tactic):
    def step(self):
        self.pickchain(Chains.Nothing)
        return
