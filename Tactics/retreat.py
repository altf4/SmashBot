import melee
import globals
import Chains
from melee.enums import Action
from Tactics.tactic import Tactic

class Retreat(Tactic):
    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        needswavedash = globals.smashbot_state.action in [Action.DOWN_B_GROUND, Action.DOWN_B_STUN, \
            Action.DOWN_B_GROUND_START, Action.LANDING_SPECIAL, Action.SHIELD, Action.SHIELD_START, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if needswavedash:
            self.pickchain(Chains.Wavedash, [1, False])
            return

        bufferzone = 30
        onright = opponent_state.x < smashbot_state.x
        if not onright:
            bufferzone *= -1

        pivotpoint = opponent_state.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        self.chain = None
        self.pickchain(Chains.DashDance, [globals.opponent_state.x + pivotpoint])
