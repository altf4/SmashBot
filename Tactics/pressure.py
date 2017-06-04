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
        self.shinemax = random.randint(4, 10)
        self.shinecount = 0
        # 50/50 chance of waveshining back into range if we get too far
        self.waveshine = bool(random.getrandbits(1))

    # We can shield pressuring if...
    def canpressure():
        # Opponent must be shielding
        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        sheilding = globals.opponent_state.action in shieldactions

        # We must be in upsmash range
        #TODO: Wrap this up somewhere
        inrange = globals.gamestate.distance < 14.5

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

        # Keep a running count of how many shines we've done
        if globals.smashbot_state.action == Action.DOWN_B_GROUND_START and \
            globals.smashbot_state.action_frame == 2:
            self.shinecount += 1

        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING, Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND, Action.KNEE_BEND]
        canshine = globals.smashbot_state.action in shineablestates
        if not canshine:
            # Dash dance at our opponent
            self.chain = None
            self.pickchain(Chains.DashDance, [globals.opponent_state.x])
            return

        inrange = globals.gamestate.distance < 11.80
        if inrange and (self.shinecount < self.shinemax):
            # Multishine
            self.pickchain(Chains.Multishine)
            return
        else:
            if self.waveshine:

                self.pickchain(Chains.Waveshine, [.7])
            else:
                self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.DOWN])
            return
