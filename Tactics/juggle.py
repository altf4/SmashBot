import melee
import Chains
from melee.enums import Action, Character
from Tactics.tactic import Tactic
from Chains.tilt import TILT_DIRECTION
from Chains.grabandthrow import THROW_DIRECTION
from Chains.airattack import AirAttack, AIR_ATTACK_DIRECTION
from Tactics.punish import Punish
from Tactics.infinite import Infinite
from melee.enums import Character
from melee.enums import Stage

class Juggle(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)

    def canjuggle(smashbot_state, opponent_state, gamestate, framedata, difficulty):
        if opponent_state.invulnerability_left > 0:
            return False

        # If the opponent is in hitstun, in the air
        if (not opponent_state.on_ground) and (opponent_state.hitstun_frames_left > 0):
            return True

        # Stop the juggle once at kill percent
        if opponent_state.percent > Infinite.killpercent(gamestate.stage, opponent_state.character):
            return False

        # If opponent is rolling and we can start a juggle combo from it
        if framedata.is_roll(opponent_state.character, opponent_state.action):
            if opponent_state.character in [Character.FOX, Character.FALCO, Character.JIGGLYPUFF, Character.PIKACHU]:
                return True

        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        # If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        # Get over to where they will end up at the end of hitstun
        end_x, end_y = self.framedata.project_hit_location(opponent_state)
        frames_left = opponent_state.hitstun_frames_left

        if self.framedata.is_roll(opponent_state.character, opponent_state.action):
            end_x = self.framedata.roll_end_position(opponent_state, gamestate.stage)
            frames_left = self.framedata.last_roll_frame(opponent_state.character, opponent_state.action) - opponent_state.action_frame

        facing_away = (smashbot_state.position.x < end_x) != smashbot_state.facing
        if smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
            facing_away = not facing_away

        on_ground = opponent_state.on_ground or opponent_state.position.y < 1 or opponent_state.action in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN]

        # Make sure we don't dashdance off the platform during a juggle
        side_platform_height, side_platform_left, side_platform_right = melee.side_platform_position(smashbot_state.position.x > 0, gamestate.stage)
        top_platform_height, top_platform_left, top_platform_right = melee.top_platform_position(gamestate.stage)
        if smashbot_state.position.y < 5:
            end_x = min(end_x, melee.EDGE_GROUND_POSITION[gamestate.stage]-5)
            end_x = max(end_x, -melee.EDGE_GROUND_POSITION[gamestate.stage]+5)
        elif (side_platform_height is not None) and abs(smashbot_state.position.y - side_platform_height) < 5:
            end_x = min(end_x, side_platform_right-5)
            end_x = max(end_x, side_platform_left+5)
        elif (top_platform_height is not None) and abs(smashbot_state.position.y - top_platform_height) < 5:
            end_x = min(end_x, top_platform_right-5)
            end_x = max(end_x, top_platform_left+5)

        # TODO Slideoff detection

        if self.logger:
            self.logger.log("Notes", " Predicted End Position: " + str(end_x) + " " + str(end_y) + " ", concat=True)
            self.logger.log("Notes", " on_ground: " + str(on_ground), concat=True)
            self.logger.log("Notes", " frames left: " + str(frames_left) + " ", concat=True)

        # Need to pivot the uptilt
        # Uptilt's hitbox is pretty forgiving if we do it a few frames early, so no big deal there
        if not on_ground:
            # If we can just throw out an uptilt and hit now, do it. No need to wait for them to fall further
            end_early_x, end_early_y = self.framedata.project_hit_location(opponent_state, 7)
            self.logger.log("Notes", " uptilt early End Position: " + str(end_early_x) + " " + str(end_early_y) + " ", concat=True)
            in_range = (abs(end_early_x - smashbot_state.position.x) < 8) and (abs(end_early_y - smashbot_state.position.y) < 12)
            if smashbot_state.action == Action.TURNING and in_range and (7 <= frames_left <= 9):
                self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                return
            # Check each height level, can we do an up-air right now?
            for height_level in AirAttack.height_levels():
                height = AirAttack.attack_height(height_level)
                commitment = AirAttack.frame_commitment(height)
                end_early_x, end_early_y = self.framedata.project_hit_location(opponent_state, commitment)
                if (commitment < frames_left) and (abs(smashbot_state.position.x - end_early_x) < 20) and (abs(end_early_y - height) < 5):
                    if self.logger:
                        self.logger.log("Notes", " Early End Position: " + str(end_early_x) + " " + str(end_early_y) + " ", concat=True)
                        self.logger.log("Notes", " height: " + str(height), concat=True)
                        self.logger.log("Notes", " commitment: " + str(commitment), concat=True)
                    self.chain = None
                    self.pickchain(Chains.AirAttack, [end_early_x, end_early_y, AIR_ATTACK_DIRECTION.UP])
                    return
            # Just dash dance to where they will end up
            # TODO board platform to get closer?
            if frames_left > 9:
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return
        else:
            if self.framedata.is_roll(opponent_state.character, opponent_state.action):
                # We still have plenty of time, so just get closer to the DD spot
                #   Even if we're already close
                if frames_left > 10:
                    # Do we need to jump up to the side platform?
                    side_plat_height, side_plat_left, side_plat_right = melee.side_platform_position(opponent_state.position.x > 0, gamestate.stage)
                    # TODO 13 is the fastest getup attack of the legal character, do a lookup for the actual one
                    if opponent_state.action in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN]:
                        frames_left += 13
                    if side_plat_height is not None and (frames_left > 25) and abs(side_plat_height - opponent_state.position.y) < 5:
                        # But only if we're already mostly there
                        smashbot_on_side_plat = smashbot_state.on_ground and abs(smashbot_state.position.y - side_plat_height) < 5
                        if side_plat_left < smashbot_state.position.x < side_plat_right:
                            self.chain = None
                            self.pickchain(Chains.BoardSidePlatform, [opponent_state.position.x > 0, False])
                            return

                    if self.logger:
                        self.logger.log("Notes", " DD at: " + str(end_x), concat=True)
                        self.logger.log("Notes", " plat at: " + str(side_plat_left) + " " + str(side_plat_right), concat=True)
                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return
                # We need to get to a position where our back is to the end position. We'll do a pivot stand to get there
                if (abs(smashbot_state.position.x - end_x) < 5):
                    # Pivot
                    if smashbot_state.action == Action.DASHING:
                        self.chain = None
                        self.pickchain(Chains.Run, [not smashbot_state.facing])
                        return
                    if smashbot_state.action in [Action.TURNING, Action.STANDING]:
                        if 7 <= frames_left <= 9:
                            if facing_away and gamestate.distance < 20:
                                self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                                return
                            else:
                                # Can't grab a tech miss. Don't try
                                if opponent_state.action not in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN] and gamestate.distance < 10:
                                    self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.UP])
                                    return
                        if frames_left == 1 and gamestate.distance < 10:
                            self.pickchain(Chains.Waveshine)
                            return
                        else:
                            self.pickchain(Chains.Nothing)
                            return

                # If we're a little further away than 5 units, but still in range
                elif (abs(smashbot_state.position.x - end_x) < 10):
                    # Don't dashdance here. Just stand still
                    if smashbot_state.action == Action.TURNING and smashbot_state.action_frame > 1:
                        self.pickchain(Chains.Nothing)
                        return

                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return

                # We're further than 5 units away, so DD into their end position
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return

        self.chain = None
        self.pickchain(Chains.DashDance, [end_x])
