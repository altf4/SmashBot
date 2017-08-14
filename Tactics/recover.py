import melee
import globals
import Chains
import random
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.firefox import FIREFOX

class Recover(Tactic):
    # Do we need to recover?
    def needsrecovery():

        # If we're on stage, then we don't need to recover
        if not globals.smashbot_state.off_stage:
            return False

        # We can now assume that we're off the stage...

        # If opponent is on stage
        if not globals.opponent_state.off_stage:
            return True

        # If opponent is in hitstun, then recover
        if globals.opponent_state.off_stage and globals.opponent_state.hitstun_frames_left > 0:
            return True

        # If opponent is closer to the edge, recover
        if globals.opponent_state.off_stage and (abs(globals.smashbot_state.x) > abs(globals.opponent_state.x)):
            return True

        return False

    def __init__(self):
        # We need to decide how we want to recover
        self.useillusion = bool(random.randint(0, 1))


    def step(self):
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        # If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        # If we can't possibly illusion to recover, don't try
        if smashbot_state.y < -15 and smashbot_state.jumps_left == 0 and smashbot_state.speed_y_self < 0:
            self.useillusion = False

        diff_x = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        # If we're ligned up, do the illusion
        #   88 is a little longer than the illusion max length
        if self.useillusion and (-15 < smashbot_state.y < 0) and (diff_x < 88):
            self.pickchain(Chains.Illusion)
            return

        # First jump back to the stage
        if smashbot_state.jumps_left > 0:
            self.pickchain(Chains.Jump)
            return

        # If we're high and doing an Illusion, just let ourselves fall into place
        if self.useillusion and smashbot_state.y > 0:
            # DI into the stage
            x = 0
            if smashbot_state.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # Don't firefox if we're super high up, wait a little to come down
        if smashbot_state.speed_y_self < 0 and smashbot_state.y < 30:
            self.pickchain(Chains.Firefox)
            return

        # Are we in range to grab the edge right now, but are moving upwards?
        facinginwards = (smashbot_state.x < 0) == smashbot_state.facing
        inedgegrabrange = diff_x < 4.5 and (-15 < smashbot_state.y < -5)
        if smashbot_state.speed_y_self > 0 and inedgegrabrange and facinginwards:
            self.pickchain(Chains.Firefox, [FIREFOX.EDGE])
            return

        # DI into the stage
        x = 0
        if smashbot_state.x < 0:
            x = 1
        self.chain = None
        self.pickchain(Chains.DI, [x, 0.5])
