import melee
import globals
import Tactics
from melee.enums import Action, Button
from Strategies.strategy import Strategy
from Tactics.punish import Punish
from Tactics.pressure import Pressure
from Tactics.defend import Defend

class Bait(Strategy):
    def __str__(self):
        string = "Bait"

        if not self.tactic:
            return string
        string += str(type(self.tactic))

        if not self.tactic.chain:
            return string
        string += str(type(self.tactic.chain))
        return string

    def step(self):
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        # Always interrupt if we got hit. Whatever chain we were in will have been broken anyway
        grabbedactions = [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, Action.GRAB_PUMMELED]
        if smashbot_state.action in grabbedactions:
            self.picktactic(Tactics.Defend)
            return

        if self.tactic and not self.tactic.isinteruptible():
            self.tactic.step()
            return

        # TODO: Maybe we need to put a check for projectiles specifically up here ahead of punish

        # If we can punish our opponent for a laggy move, let's do that
        if Punish.canpunish():
            self.picktactic(Tactics.Punish)
            return

        # Do we need to defend an attack?
        if Defend.needsdefense():
            self.picktactic(Tactics.Defend)
            return

        # Can we shield pressure them?
        if Pressure.canpressure():
            self.picktactic(Tactics.Pressure)
            return

        # Is opponent shielding?
        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        # Is opponent starting a jump?
        earlyjumpactions = [Action.KNEE_BEND, Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]
        if opponent_state.action in shieldactions or opponent_state.action in earlyjumpactions:
            self.picktactic(Tactics.Approach)
            return

        self.picktactic(Tactics.KeepDistance)
