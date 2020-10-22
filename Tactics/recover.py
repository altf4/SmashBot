import melee
import Chains
import random
import math
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.firefox import FIREFOX
from Chains.illusion import SHORTEN

class Recover(Tactic):
    # Do we need to recover?
    def needsrecovery(smashbot_state, opponent_state, gamestate):
        onedge = smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING, Action.EDGE_GETUP_SLOW, \
        Action.EDGE_GETUP_QUICK, Action.EDGE_ATTACK_SLOW, Action.EDGE_ATTACK_QUICK, Action.EDGE_ROLL_SLOW, Action.EDGE_ROLL_QUICK]

        # If the opponent is on-stage, and Smashbot is on-edge, Smashbot needs to ledgedash
        if not opponent_state.off_stage and onedge:
            return True

        # If we're on stage, then we don't need to recover
        if not smashbot_state.off_stage:
            return False

        if smashbot_state.on_ground:
            return False

        # We can now assume that we're off the stage...

        # If opponent is dead
        if opponent_state.action in [Action.DEAD_DOWN, Action.DEAD_RIGHT, Action.DEAD_LEFT, \
                Action.DEAD_FLY, Action.DEAD_FLY_STAR, Action.DEAD_FLY_SPLATTER]:
            return True

        # If opponent is on stage
        if not opponent_state.off_stage:
            return True

        # If opponent is in hitstun, then recover, unless we're on the edge.
        if opponent_state.off_stage and opponent_state.hitstun_frames_left > 0 and not onedge:
            return True

        if opponent_state.action == Action.DEAD_FALL and opponent_state.y < -30:
            return True

        # If opponent is closer to the edge, recover
        diff_x_opponent = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(opponent_state.x))
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.x))

        # Using (opponent_state.y + 15)**2 was causing a keepdistance/dashdance bug.
        opponent_dist = math.sqrt( (opponent_state.y)**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( (smashbot_state.y)**2 + (diff_x)**2 )

        if opponent_dist < smashbot_dist and not onedge:
            return True

        # If opponent is ON the edge, recover
        if opponentonedge and not onedge:
            return True

        return False

    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        # We need to decide how we want to recover
        self.useillusion = bool(random.randint(0, 1))


    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING, Action.EDGE_GETUP_SLOW, \
        Action.EDGE_GETUP_QUICK, Action.EDGE_ATTACK_SLOW, Action.EDGE_ATTACK_QUICK, Action.EDGE_ROLL_SLOW, Action.EDGE_ROLL_QUICK]

        # If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            self.pickchain(Chains.Edgedash)
            return

        # If we can't possibly illusion to recover, don't try
        if smashbot_state.y < -15 and smashbot_state.jumps_left == 0 and smashbot_state.speed_y_self < 0:
            self.useillusion = False

        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.x))

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

        # If we can just do nothing and grab the edge, do that
        if -12 < smashbot_state.y and (diff_x < 10) and facinginwards and smashbot_state.speed_y_self < 0:
            # Do a Fastfall if we're not already
            if smashbot_state.action == Action.FALLING and smashbot_state.speed_y_self > -3.3:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0])
                return

            # If we are currently moving away from the stage, DI in
            # MIGHT NEED ADJUSTMENT FOR BF, MIGHT NOT
            if (smashbot_state.speed_air_x_self > 0) == (smashbot_state.x > 0):
                x = 0
                if smashbot_state.x < 0:
                    x = 1
                self.chain = None
                self.pickchain(Chains.DI, [x, 0.5])
                return
            else:
                self.pickchain(Chains.Nothing)
                return

        # Illusion grabs ledge faster than firefox does.
        # This can come in handy after Marth jabs Fox out of his recovery. Fox can just fall to the appropriate height & grab ledge with illusion.
        if (-16.4 < smashbot_state.y < -5) and (10 < diff_x < 88) and not opponentonedge:
            length = SHORTEN.LONG
            if diff_x < 50:
                length = SHORTEN.MID
            if diff_x < 40:
                length = SHORTEN.MID_SHORT
            if diff_x < 31:
                length = SHORTEN.SHORT

            self.pickchain(Chains.Illusion, [length])
            return

        # If we illusion at this range when the opponent is holding ledge, Smashbot dies.
        # Firefox instead if the opponent is grabbing edge. Opponent has to get up or get burned.
        if (-16.4 < smashbot_state.y < -5) and (diff_x < 10) and facinginwards and opponentonedge:
            self.pickchain(Chains.Firefox, [FIREFOX.MEDIUM])
            return

        # If we're lined up, do the illusion
        #   88 is a little longer than the illusion max length
        if self.useillusion and (-16.4 < smashbot_state.y < -5) and (10 < diff_x < 88):
            length = SHORTEN.LONG
            if diff_x < 50:
                length = SHORTEN.MID
            if diff_x < 40:
                length = SHORTEN.MID_SHORT
            if diff_x < 31:
                length = SHORTEN.SHORT

            self.pickchain(Chains.Illusion, [length])
            return

        # Is the opponent going offstage to edgeguard us?
        opponent_edgedistance = abs(opponent_state.x) - abs(melee.stages.EDGE_GROUND_POSITION[gamestate.stage])
        opponentxvelocity = opponent_state.speed_air_x_self + opponent_state.speed_ground_x_self
        opponentmovingtoedge = (opponent_edgedistance < 20) and (opponentxvelocity > 0 == opponent_state.x > 0)
        opponentgoingoffstage = opponent_state.action in [Action.FALLING, Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD, Action.LANDING_SPECIAL,\
        Action.DASHING, Action.WALK_MIDDLE, Action.WALK_FAST, Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR, Action.DAIR]

        x_canairdodge = abs(smashbot_state.x) - 18 <= abs(melee.stages.EDGE_GROUND_POSITION[gamestate.stage])
        y_canairdodge = smashbot_state.y + 18 >= -6
        x = 0
        if smashbot_state.x < 0:
            x = 1
        if x_canairdodge and y_canairdodge and opponentgoingoffstage:
            self.pickchain(Chains.Airdodge, [x, 1])
            return

        # First jump back to the stage if we're low
        # Fox can at least DJ from y = -55.43 and still sweetspot grab the ledge.
        # For reference, if Fox inputs a DJ at y = -58.83, he will NOT sweetspot grab the ledge.
        if (smashbot_state.jumps_left > 0 and smashbot_state.y < -52) or opponentgoingoffstage or opponentmovingtoedge:
            self.pickchain(Chains.Jump)
            return

        # If we're high and doing an Illusion, just let ourselves fall into place
        if self.useillusion and smashbot_state.y > -5:
            # DI into the stage
            x = 0
            if smashbot_state.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # Don't firefox if we're super high up, wait a little to come down
        if smashbot_state.speed_y_self < 0 and smashbot_state.y < -60:
            self.pickchain(Chains.Firefox)
            return

        # DI into the stage
        # NEEDS ADJUSTMENT FOR BF
        battlefielded = (smashbot_state.x < melee.stages.EDGE_POSITION[gamestate.stage] + 13) and gamestate.stage == melee.enums.Stage.BATTLEFIELD
        if not battlefielded:
            x = 0
            if smashbot_state.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
