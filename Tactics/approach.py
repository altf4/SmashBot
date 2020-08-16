import melee
import Chains
from melee.enums import Action, Button
from Tactics.tactic import Tactic

class Approach(Tactic):
    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        needswavedash = smashbot_state.action in [Action.DOWN_B_GROUND, Action.DOWN_B_STUN, \
            Action.DOWN_B_GROUND_START, Action.LANDING_SPECIAL, Action.SHIELD, Action.SHIELD_START, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if needswavedash:
            self.pickchain(Chains.Wavedash)
            return

        # If opponent is on a side platform and we're not
        on_main_platform = smashbot_state.y < 1 and smashbot_state.on_ground
        if opponent_state.y > 1 and opponent_state.on_ground and on_main_platform:
            self.pickchain(Chains.BoardSidePlatform, [opponent_state.x > 0])
            return

        self.chain = None
        self.pickchain(Chains.DashDance, [opponent_state.x])
