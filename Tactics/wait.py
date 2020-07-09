import melee
import Chains
from Tactics.tactic import Tactic
from melee.enums import Action

class Wait(Tactic):
    def shouldwait(smashbot_state, framedata):
        # Make an exception for shine states, since we're still actionable for them
        if smashbot_state.action in [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND, Action.DOWN_B_STUN]:
            return False

        # If we're in the cooldown for an attack, just do nothing.
        if framedata.attack_state(smashbot_state.character, smashbot_state.action, smashbot_state.action_frame) == melee.enums.AttackState.COOLDOWN:
            return True

        if smashbot_state.action in [Action.BACKWARD_TECH, Action.NEUTRAL_TECH, Action.FORWARD_TECH, \
                Action.TECH_MISS_UP, Action.EDGE_GETUP_QUICK, Action.EDGE_GETUP_SLOW, Action.EDGE_ROLL_QUICK, \
                Action.EDGE_ROLL_SLOW, Action.SHIELD_STUN, Action.TECH_MISS_DOWN]:
            return True

        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        self.pickchain(Chains.Nothing)
        return
