import melee
import globals
import Chains
from Tactics.tactic import Tactic

class Punish(Tactic):
    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()

        #Otherwise, kill the existing chain and start a new one
        self.chain = None

        self.pickchain(Chains.DashDance, [globals.opponent_state.x])
