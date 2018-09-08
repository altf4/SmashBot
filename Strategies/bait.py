import melee
import Tactics
import random
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
from Tactics.retreat import Retreat

class Bait(Strategy):
    def __init__(self, gamestate, smashbot_state, opponent_state, logger, controller, framedata, difficulty):
        self.approach = False
        self.gamestate = gamestate
        self.smashbot_state = smashbot_state
        self.opponent_state = opponent_state
        self.logger = logger
        self.controller = controller
        self.framedata = framedata
        self.difficulty = difficulty

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
        # If we have stopped approaching, reset the state
        if type(self.tactic) != Tactics.Approach:
            self.approach = False

        if Mitigate.needsmitigation(self.smashbot_state):
            self.picktactic(Tactics.Mitigate)
            return

        if self.tactic and not self.tactic.isinteruptible():
            self.tactic.step()
            return

        # If we're stuck in a lag state, just do nothing. Trying an action might just
        #   buffer an input we don't want
        if Wait.shouldwait(self.smashbot_state, self.framedata):
            self.picktactic(Tactics.Wait)
            return

        if Recover.needsrecovery(self.smashbot_state, self.opponent_state, self.gamestate):
            self.picktactic(Tactics.Recover)
            return

        if Celebrate.deservescelebration(self.smashbot_state, self.opponent_state):
            self.picktactic(Tactics.Celebrate)
            return

        # Difficulty 5 is a debug / training mode
        #   Don't do any attacks, and don't do any shielding
        #   Take attacks, DI, and recover
        if self.difficulty == 5:
            self.picktactic(Tactics.KeepDistance)
            return

        if Defend.needsprojectiledefense(self.smashbot_state, self.opponent_state, self.gamestate):
            self.picktactic(Tactics.Defend)
            return

        # If we can infinite our opponent, do that!
        if Infinite.caninfinite(self.smashbot_state, self.opponent_state, self.gamestate, self.framedata, self.difficulty):
            self.picktactic(Tactics.Infinite)
            return

        # If we can punish our opponent for a laggy move, let's do that
        if Punish.canpunish(self.smashbot_state, self.opponent_state, self.gamestate, self.framedata):
            self.picktactic(Tactics.Punish)
            return

        # Do we need to defend an attack?
        if Defend.needsdefense(self.smashbot_state, self.opponent_state, self.gamestate, self.framedata):
            self.picktactic(Tactics.Defend)
            return

        # Can we edge guard them?
        if Edgeguard.canedgeguard(self.smashbot_state, self.opponent_state, self.gamestate):
            self.picktactic(Tactics.Edgeguard)
            return

        # Can we shield pressure them?
        if Pressure.canpressure(self.opponent_state, self.gamestate):
            self.picktactic(Tactics.Pressure)
            return

        if Retreat.shouldretreat(self.smashbot_state, self.opponent_state, self.gamestate):
            self.picktactic(Tactics.Retreat)
            return

        # Is opponent starting a jump?
        jumping = self.opponent_state.action == Action.KNEE_BEND
        if self.opponent_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] and \
                self.opponent_state.speed_y_self > 0:
            jumping = True

        # Randomly approach some times rather than keeping distance
        if self.smashbot_state.action == Action.TURNING and random.randint(0, 40) == 0:
            self.approach = True

        if (jumping and self.opponent_state.invulnerability_left <= 0) or self.approach:
            self.picktactic(Tactics.Approach)
            return

        self.picktactic(Tactics.KeepDistance)
