import melee
import globals
import Chains
from melee.enums import Action, Button
from Tactics.tactic import Tactic

class Punish(Tactic):

    # Static function that returns whether we have enough time to run in and punish,
    # given the current gamestate. Either a shine or upsmash
    def canpunish():
        # Can we shine right now without any movement?
        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING]

        #TODO: Wrap the shine range into a helper
        foxshinerange = 11.8
        inshinerange = globals.gamestate.distance < foxshinerange

        if inshinerange and globals.smashbot_state.action in shineablestates:
            return True

        #TODO: Handle rolling here as well. This only currently considers attacks

        #TODO: Wrap this up into a helper
        foxrunspeed = 2.2

        # How many frames do we have to work with?
        firsthitbox = globals.framedata.firsthitboxframe(globals.opponent_state.character, \
            globals.opponent_state.action)
        framesleft = firsthitbox - globals.opponent_state.action_frame

        if framesleft < 1:
            return False

        #TODO: Subtract from this time spent turning or transitioning
        # Assume that we can run at max speed toward our opponent
        # We can only run for framesleft-1 frames, since we have to spend at least one attacking
        potentialrundistance = (framesleft-1) * foxrunspeed

        if globals.gamestate.distance - potentialrundistance < foxshinerange:
            return True

        return False

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        #TODO: Wrap the shine range into a helper
        foxshinerange = 11.8
        if globals.gamestate.distance < foxshinerange:
            self.pickchain(Chains.Waveshine)
            return

        # Kill the existing chain and start a new one
        self.chain = None
        self.pickchain(Chains.DashDance, [globals.opponent_state.x])
