import melee
import globals
import Chains
import random
from melee.enums import Action, Button
from Tactics.tactic import Tactic
from Chains.grabandthrow import THROW_DIRECTION

# Shield pressure
class Pressure(Tactic):
    def __init__(self):
        # Pick a random max number of shines
        self.shinemax = random.randint(5, 10)
        self.shinecount = 0

        self.waveshine = False
        self.shffl = False
        self.dashdance = False

        # Remove the dash dance from the random pool if we're in a spot where it would be bad
        dashchance = 2
        if globals.smashbot_state not in [Action.STANDING, Action.TURNING, Action.DASHING]:
            dashchance = 0

        # What sort of shield pressure should this be? Pick one at random
        rand = random.choice([1]*5 + [2]*3 + [3]*dashchance)

        # If we're on our last 2 stocks, only do dash dance
        if globals.smashbot_state.stock <= 2:
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
    def canpressure():
        # Opponent must be shielding
        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        sheilding = globals.opponent_state.action in shieldactions

        if globals.opponent_state.invulnerability_left > 0:
            return False

        # We must be in upsmash range
        #TODO: Wrap this up somewhere
        inrange = globals.gamestate.distance < 20

        # We must be facing our opponent
        onright = globals.opponent_state.x < globals.smashbot_state.x
        facing = globals.smashbot_state.facing
        # When we're turning, the facing bool is sorta backwards
        if globals.smashbot_state.action == Action.TURNING:
            facing = not facing
        facingopponent = facing != onright

        return sheilding and inrange and facingopponent

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        if self.dashdance:
            self.chain = None
            if globals.smashbot_state.action in [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]:
                distance = max(globals.gamestate.distance / 20, 1)
                self.pickchain(Chains.Wavedash, [distance])
                return
            self.pickchain(Chains.DashDance, [globals.opponent_state.x])
            return

        # Keep a running count of how many shines we've done
        if globals.smashbot_state.action == Action.DOWN_B_GROUND_START and \
            globals.smashbot_state.action_frame == 2:
            self.shinecount += 1

        canshine = globals.smashbot_state.action in [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING, Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND, Action.KNEE_BEND]

        candash = globals.smashbot_state.action in [Action.DASHING, Action.TURNING, Action.RUNNING, \
            Action.EDGE_TEETERING_START, Action.EDGE_TEETERING]

        if not canshine and candash:
            # Dash dance at our opponent
            self.chain = None
            self.pickchain(Chains.DashDance, [globals.opponent_state.x])
            return

        #TODO: Wrap this up somewhere
        # If we're out of grab range, wavedash in far
        if globals.gamestate.distance > 13.5:
            self.pickchain(Chains.Wavedash)
            return

        # TODO: Wrap this up somewhere
        inrange = globals.gamestate.distance < 11.80-3
        if inrange and (self.shinecount < self.shinemax):
            # Multishine
            self.pickchain(Chains.Multishine)
            return
        else:
            if not inrange:
                # How do we get back into range? Wavedash or SHFFL?
                if self.waveshine:
                    x = 0.5
                    # If opponent is facing us, do the max distance wavedash to cross them up (avoid grab)
                    if (globals.opponent_state.x < globals.smashbot_state.x) == globals.opponent_state.facing:
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

            self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.DOWN])
            return
