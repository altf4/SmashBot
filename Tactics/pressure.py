import melee
import Chains
import random
from melee.enums import Action, Button
from Tactics.tactic import Tactic
from Chains.grabandthrow import THROW_DIRECTION

# Shield pressure
class Pressure(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        # Pick a random max number of shines
        self.shinemax = random.randint(0, 8)
        self.shinecount = 0

        self.waveshine = False
        self.shffl = False
        self.dashdance = False

        dashchance = 2
        # TODO Remove the dash dance from the random pool if we're in a spot where it would be bad
        # if self.smashbot_state.action not in [Action.STANDING, Action.TURNING, Action.DASHING]:
        #     dashchance = 0

        # What sort of shield pressure should this be? Pick one at random
        rand = random.choice([1]*5 + [2]*3 + [3]*dashchance)

        # On difficulty 1 and 2, only do dash dance
        if self.difficulty <= 2:
            rand = 3

        # 50% chance of being SHFFL style pressure
        if rand == 1:
            self.shffl = True
        # 30% chance of being waveshine style pressure
        if rand == 2:
            self.waveshine = True
        # 20% chance of being dashdance style pressure
        if rand == 3:
            self.dashdance = True

    # We can shield pressuring if...
    def canpressure(opponent_state, gamestate):
        # Opponent must be shielding
        shieldactions = [Action.SHIELD_START, Action.SHIELD, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        sheilding = opponent_state.action in shieldactions

        if opponent_state.invulnerability_left > 0:
            return False

        # We must be in close range
        inrange = gamestate.distance < 30

        return sheilding and inrange

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        if self.dashdance:
            self.chain = None
            # Don't try to dashdance if we know we can't
            if smashbot_state.action in [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]:
                distance = max(gamestate.distance / 20, 1)
                self.pickchain(Chains.Wavedash, [distance])
                return
            self.pickchain(Chains.DashDance, [opponent_state.x])
            return

        # Keep a running count of how many shines we've done
        if smashbot_state.action == Action.DOWN_B_GROUND_START and \
            smashbot_state.action_frame == 2:
            self.shinecount += 1

        canshine = smashbot_state.action in [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING, Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND, Action.KNEE_BEND]

        candash = smashbot_state.action in [Action.DASHING, Action.TURNING, Action.RUNNING, \
            Action.EDGE_TEETERING_START, Action.EDGE_TEETERING]

        inshinerange = gamestate.distance < 11.80-3
        # Where will opponent end up, after sliding is accounted for? (at the end of our grab)
        endposition = opponent_state.x + self.framedata.slidedistance(opponent_state, opponent_state.speed_ground_x_self, 7)
        ourendposition = smashbot_state.x + self.framedata.slidedistance(smashbot_state, smashbot_state.speed_ground_x_self, 7)
        ingrabrange = abs(endposition - ourendposition) < 13.5

        # If we're out of range, and CAN dash, then let's just dash in no matter
        #   what other options are here.
        if not inshinerange and candash:
            # Dash dance at our opponent
            self.chain = None
            self.pickchain(Chains.DashDance, [opponent_state.x])
            return

        neutral = smashbot_state.action in [Action.STANDING, Action.DASHING, Action.TURNING, \
            Action.RUNNING, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING]

        facingopponent = smashbot_state.facing == (smashbot_state.x < opponent_state.x)
        # If we're turning, then any action will turn around, so take that into account
        if smashbot_state.action == Action.TURNING:
            facingopponent = not facingopponent

        # Multishine if we're in range, facing our opponent and haven't used up all our shines
        if inshinerange and facingopponent and (self.shinecount < self.shinemax):
            self.pickchain(Chains.Multishine)
            return
        # Here's where things get complicated...
        else:
            # If we're not in range, then we need to get back into range. But how?
            #   Wavedash or SHFFL?
            if not inshinerange:
                if self.waveshine:
                    x = 0.5
                    # If opponent is facing us, do the max distance wavedash to cross them up (avoid grab)
                    if (opponent_state.x < smashbot_state.x) == opponent_state.facing:
                        x = 1.0
                    self.chain = None
                    self.pickchain(Chains.Waveshine, [x])
                    shinecount = 0
                    return
                if self.shffl:
                    self.chain = None
                    self.pickchain(Chains.Shffl)
                    shinecount = 0
                    return

            # Recalculate facing for the slide end
            facingopponent = smashbot_state.facing == (ourendposition < endposition)

            # Grab opponent
            if ingrabrange and facingopponent and (self.shinecount >= self.shinemax):
                self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.DOWN])
                return

        # If we fall through, then just dashdance at our opponent
        self.chain = None
        self.pickchain(Chains.DashDance, [opponent_state.x])
