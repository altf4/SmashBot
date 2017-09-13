import melee
import globals
import Tactics
from melee.enums import Action, Button
from Strategies.strategy import Strategy
from Tactics.punish import Punish
from Tactics.pressure import Pressure
from Tactics.defend import Defend
from Tactics.recover import Recover
from Tactics.mitigate import Mitigate
from Tactics.edgeguard import Edgeguard
from Tactics.infinite import Infinite
from Tactics.celebrate import Celebrate
from Tactics.wait import Wait

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

        if Mitigate.needsmitigation():
            self.picktactic(Tactics.Mitigate)
            return

        if self.tactic and not self.tactic.isinteruptible():
            self.tactic.step()
            return

        # If we're stuck in a lag state, just do nothing. Trying an action might just
        #   buffer an input we don't want
        if Wait.shouldwait():
            self.picktactic(Tactics.Wait)
            return

        if Recover.needsrecovery():
            self.picktactic(Tactics.Recover)
            return

        if Celebrate.deservescelebration():
            self.picktactic(Tactics.Celebrate)
            return

        # Difficulty 5 is a debug / training mode
        #   Don't do any attacks, and don't do any shielding
        #   Take attacks, DI, and recover
        if globals.difficulty == 5:
            self.picktactic(Tactics.KeepDistance)
            return

        if Defend.needsprojectiledefense():
            self.picktactic(Tactics.Defend)
            return

        # If we can infinite our opponent, do that!
        if Infinite.caninfinite():
            self.picktactic(Tactics.Infinite)
            return

        # If we can punish our opponent for a laggy move, let's do that
        if Punish.canpunish():
            self.picktactic(Tactics.Punish)
            return

        # Do we need to defend an attack?
        if Defend.needsdefense():
            self.picktactic(Tactics.Defend)
            return

        # Can we edge guard them?
        if Edgeguard.canedgeguard():
            self.picktactic(Tactics.Edgeguard)
            return

        # Can we shield pressure them?
        if Pressure.canpressure():
            self.picktactic(Tactics.Pressure)
            return

        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]

        # If opponent is landing from an attack, and we're sheilding, retreat!
        if opponent_state.action in [Action.DAIR_LANDING, Action.NAIR_LANDING, Action.FAIR_LANDING, \
                Action.UAIR_LANDING, Action.BAIR_LANDING, Action.LANDING] and smashbot_state.action in shieldactions:
            self.picktactic(Tactics.Retreat)
            return

        # Is opponent starting a jump?
        jumping = opponent_state.action == Action.KNEE_BEND
        if opponent_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] and \
                opponent_state.speed_y_self > 0:
            jumping = True

        if jumping and opponent_state.invulnerability_left <= 0:
            self.picktactic(Tactics.Approach)
            return

        self.picktactic(Tactics.KeepDistance)
