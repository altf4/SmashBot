import melee
import Chains
import random
import math
from melee.enums import Action, Stage
from Tactics.punish import Punish
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

        if opponent_state.action == Action.DEAD_FALL and opponent_state.position.y < -30:
            return True

        # If opponent is closer to the edge, recover
        diff_x_opponent = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(opponent_state.position.x))
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.position.x))

        # Using (opponent_state.position.y + 15)**2 was causing a keepdistance/dashdance bug.
        opponent_dist = math.sqrt( (opponent_state.position.y)**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( (smashbot_state.position.y)**2 + (diff_x)**2 )

        if opponent_dist < smashbot_dist and not onedge:
            return True

        if smashbot_dist >= 20:
            return True

        # If we're both fully off stage, recover
        if opponent_state.off_stage and smashbot_state.off_stage and not onedge and not opponentonedge:
            return True

        # If opponent is ON the edge, recover
        if opponentonedge and not onedge:
            return True

        return False

    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        # We need to decide how we want to recover
        self.useillusion = bool(random.randint(0, 1))
        self.logger = logger

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING, Action.EDGE_GETUP_SLOW, \
        Action.EDGE_GETUP_QUICK, Action.EDGE_ATTACK_SLOW, Action.EDGE_ATTACK_QUICK, Action.EDGE_ROLL_SLOW, Action.EDGE_ROLL_QUICK]

        # If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            # It takes 16 frames to go from frame 1 of hanging to standing.
            frames_left = Punish.framesleft(opponent_state, self.framedata, smashbot_state)
            refresh = frames_left < 16 and smashbot_state.invulnerability_left < 16
            self.pickchain(Chains.Edgedash, [refresh])
            return

        # If we can't possibly illusion to recover, don't try
        if smashbot_state.position.y < -15 and smashbot_state.jumps_left == 0 and smashbot_state.speed_y_self < 0:
            self.useillusion = False

        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.position.x))

        # If we can just grab the edge with a firefox, do that
        facinginwards = smashbot_state.facing == (smashbot_state.position.x < 0)
        if not facinginwards and smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
            facinginwards = True

        if smashbot_state.action == Action.DEAD_FALL:
            self.chain = None
            self.pickchain(Chains.DI, [int(smashbot_state.position.x < 0), 0.5])
            return

        # FireFox high
        if smashbot_state.action == Action.SWORD_DANCE_1_AIR and smashbot_state.position.y > 10:
            self.chain = None
            self.pickchain(Chains.DI, [int(smashbot_state.position.x < 0), 0.5])
            return

        # Are we facing the wrong way in shine? Turn around
        if smashbot_state.action == Action.DOWN_B_STUN and not facinginwards:
            x = 0
            if smashbot_state.position.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # If we can just do nothing and grab the edge, do that
        # Action.SWORD_DANCE_1_AIR is Fox's initial freefall after his upB finishes launching.
        # Fox can ledgegrab from behind in this animation, but he oftentimes needs to fastfall to hit the window.
        if -12 < smashbot_state.position.y and (diff_x < 10) and (facinginwards or smashbot_state.action == Action.SWORD_DANCE_1_AIR) and smashbot_state.speed_y_self <= 0:
            # Do a Fastfall if we're not already
            if smashbot_state.action == Action.FALLING and smashbot_state.speed_y_self > -3.3:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0])
                return

            # If we are currently moving away from the stage, DI in
            if (smashbot_state.speed_air_x_self > 0) == (smashbot_state.position.x > 0):
                x = 0
                if smashbot_state.position.x < 0:
                    x = 1
                self.chain = None
                self.pickchain(Chains.DI, [x, 0.5])
                return
            else:
                # Don't get battlefielded
                if smashbot_state.action == Action.SLIDING_OFF_EDGE and gamestate.stage == Stage.BATTLEFIELD:
                    self.chain = None
                    x = 0
                    if smashbot_state.position.x > 0:
                        x = 1
                    self.pickchain(Chains.DI, [x, 0.5])
                    return

                self.pickchain(Chains.Nothing)
                return

        # If we're lined up, do the illusion
        #   88 is a little longer than the illusion max length
        # Also, we have to adjust the min illusion height upwards on BF
        min_height = -16.4
        if gamestate.stage == melee.enums.Stage.BATTLEFIELD:
            min_height = -10
        if self.useillusion and (min_height < smashbot_state.position.y < -5) and (10 < diff_x < 88) and not opponentonedge:
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
        if (-16.4 < smashbot_state.position.y < -5) and (diff_x < 10) and facinginwards:
            if gamestate.stage == melee.enums.Stage.BATTLEFIELD:
                # If Smashbot does a random or horizontal sideB here, he pretty reliably SDs on Battlefield
                self.pickchain(Chains.Firefox, [FIREFOX.EDGE])
            else:
                self.pickchain(Chains.Firefox, [FIREFOX.RANDOM])
            return

        # Is the opponent going offstage to edgeguard us?
        opponent_edgedistance = abs(opponent_state.position.x) - abs(melee.stages.EDGE_GROUND_POSITION[gamestate.stage])
        opponentxvelocity = opponent_state.speed_air_x_self + opponent_state.speed_ground_x_self
        opponentmovingtoedge = not opponent_state.off_stage and (opponent_edgedistance < 20) and (opponentxvelocity > 0 == opponent_state.position.x > 0)
        opponentgoingoffstage = opponent_state.action in [Action.FALLING, Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD, Action.LANDING_SPECIAL,\
            Action.DASHING, Action.WALK_MIDDLE, Action.WALK_FAST, Action.NAIR, Action.FAIR, Action.UAIR, Action.BAIR, Action.DAIR]

        # Don't airdodge recovery if we still have attack velocity. It just causes an SD
        hit_movement = abs(smashbot_state.speed_x_attack) > 0.2

        x_canairdodge = abs(smashbot_state.position.x) - 18 <= abs(melee.stages.EDGE_GROUND_POSITION[gamestate.stage])
        y_canairdodge = smashbot_state.position.y >= -24
        if x_canairdodge and y_canairdodge and (opponentgoingoffstage or opponentmovingtoedge) and not hit_movement:
            self.pickchain(Chains.Airdodge, [int(smashbot_state.position.x < 0), int(smashbot_state.position.y + smashbot_state.ecb.bottom.y < 5)])
            return

        # Jump if we're falling, are below stage, and have a jump
        if smashbot_state.speed_y_self < 0 and smashbot_state.jumps_left > 0 and smashbot_state.position.y < 0:
            self.pickchain(Chains.Jump)
            return

        # First jump back to the stage if we're low
        # Fox can at least DJ from y = -55.43 and still sweetspot grab the ledge.
        # For reference, if Fox inputs a DJ at y = -58.83, he will NOT sweetspot grab the ledge.
        jump_randomizer = random.randint(0, 5) == 1
        if smashbot_state.jumps_left > 0 and (smashbot_state.position.y < -52 or opponentgoingoffstage or opponentmovingtoedge or jump_randomizer):
            self.pickchain(Chains.Jump)
            return

        # Always just jump out of shine
        if smashbot_state.action == Action.DOWN_B_AIR:
            self.pickchain(Chains.Jump)
            return

        # If we're high and doing an Illusion, just let ourselves fall into place
        if self.useillusion and smashbot_state.position.y > -5:
            # DI into the stage
            x = 0
            if smashbot_state.position.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # The height to start a firefox at
        firefox_height = -60 + random.randint(0, 30)

        # If opponent is in hitstun, just do it now
        if opponent_state.hitstun_frames_left > 0:
            firefox_height = 100

        # Don't firefox if we're super high up, wait a little to come down
        if smashbot_state.speed_y_self < 0 and smashbot_state.position.y < firefox_height:
            if gamestate.stage == melee.enums.Stage.BATTLEFIELD and diff_x < 30:
                self.pickchain(Chains.Firefox, [FIREFOX.HIGH])
            else:
                self.pickchain(Chains.Firefox, [FIREFOX.SAFERANDOM])
            return

        randomhighrecovery = smashbot_state.position.y > 0 and random.randint(0, 3) == 1
        if randomhighrecovery:
            if bool(random.randint(0, 1)):
                self.pickchain(Chains.Firefox, [FIREFOX.RANDOM])
            else:
                self.pickchain(Chains.Illusion, [SHORTEN.LONG])
            return

        # DI into the stage
        battlefielded = (smashbot_state.position.x < melee.stages.EDGE_POSITION[gamestate.stage] + 13) and gamestate.stage == melee.enums.Stage.BATTLEFIELD and smashbot_state.position.y < 0
        if not battlefielded:
            x = 0
            if smashbot_state.position.x < 0:
                x = 1
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
