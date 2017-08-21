import melee
import globals
import Chains
import random
import math
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.firefox import FIREFOX

class Recover(Tactic):
    # Do we need to recover?
    def needsrecovery():
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        onedge = globals.smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = globals.opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        if not opponent_state.off_stage and onedge:
            return True

        # If we're on stage, then we don't need to recover
        if not smashbot_state.off_stage:
            return False

        if smashbot_state.on_ground:
            return False

        # We can now assume that we're off the stage...

        # If opponent is on stage
        if not opponent_state.off_stage:
            return True

        # If opponent is in hitstun, then recover, unless we're on the edge.
        if opponent_state.off_stage and opponent_state.hitstun_frames_left > 0 and not onedge:
            return True

        if opponent_state.action == Action.DEAD_FALL and opponent_state.y < -20:
            return True

        # If opponent is closer to the edge, recover
        diff_x_opponent = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(opponent_state.x))
        diff_x = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        opponent_dist = math.sqrt( opponent_state.y**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( smashbot_state.y**2 + (diff_x)**2 )

        if opponent_dist < smashbot_dist:
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

        if globals.smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            self.pickchain(Chains.Edgedash)
            return

        # If we can't possibly illusion to recover, don't try
        if smashbot_state.y < -15 and smashbot_state.jumps_left == 0 and smashbot_state.speed_y_self < 0:
            self.useillusion = False

        diff_x = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        # If we can just grab the edge with a firefox, do that
        facinginwards = smashbot_state.facing == (smashbot_state.x < 0)
        if not facinginwards and smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
            facinginwards = True

        if smashbot_state.action == Action.DEAD_FALL:
            x = 0
            if smashbot_state.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # Are we facing the wrong way in shine? Turn around
        if smashbot_state.action == Action.DOWN_B_STUN and not facinginwards:
            x = 0
            if smashbot_state.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        if (-15 < smashbot_state.y < -5) and (diff_x < 10) and facinginwards:
            self.pickchain(Chains.Firefox, [FIREFOX.MEDIUM])
            return

        # If we can just do nothing and grab the edge, do that
        if -5 < smashbot_state.y and (diff_x < 10) and facinginwards and smashbot_state.speed_y_self < 0:
            self.pickchain(Chains.Nothing)
            return

        # If we're ligned up, do the illusion
        #   88 is a little longer than the illusion max length
        if self.useillusion and (-15 < smashbot_state.y < 0) and (diff_x < 88):
            self.pickchain(Chains.Illusion)
            return

        # First jump back to the stage if we're low
        if smashbot_state.jumps_left > 0 and smashbot_state.y < -20:
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

        # DI into the stage
        x = 0
        if smashbot_state.x < 0:
            x = 1
        self.chain = None
        self.pickchain(Chains.DI, [x, 0.5])
