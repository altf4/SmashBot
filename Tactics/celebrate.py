import melee
import Chains
from melee.enums import Action, Character
from Tactics.tactic import Tactic

class Celebrate(Tactic):
    def deservescelebration(smashbot_state, opponent_state):
        if smashbot_state.off_stage:
            return False

        if opponent_state.action in [Action.DEAD_FLY_STAR, Action.DEAD_FLY_SPLATTER, Action.DEAD_FLY, \
                Action.DEAD_LEFT, Action.DEAD_RIGHT, Action.DEAD_DOWN]:
            return True

        if opponent_state.action == Action.DEAD_FALL and opponent_state.position.y < -20:
            return True

        if opponent_state.action == Action.PARASOL_FALLING and opponent_state.character == Character.PEACH and \
                opponent_state.position.y < -30:
            return True

        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)
        if smashbot_state.action == Action.EDGE_HANGING:
            self.chain = None
            self.pickchain(Chains.DI, [0.5, 0.65])
            return

        self.pickchain(Chains.Multishine)
        return
