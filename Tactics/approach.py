import melee
import globals
import Chains
from melee.enums import Action, Button
from Tactics.tactic import Tactic

class Approach(Tactic):
    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        needswavedash = globals.smashbot_state.action in [Action.DOWN_B_GROUND, Action.DOWN_B_STUN, \
            Action.DOWN_B_GROUND_START, Action.LANDING_SPECIAL, Action.SHIELD, Action.SHIELD_START, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if needswavedash:
            self.pickchain(Chains.Wavedash)
            return

        self.chain = None
        self.pickchain(Chains.DashDance, [globals.opponent_state.x])
