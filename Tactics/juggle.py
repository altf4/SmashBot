import melee
import Chains
from melee.enums import Action, Character
from Tactics.tactic import Tactic
from Chains.tilt import TILT_DIRECTION
from Chains.grabandthrow import THROW_DIRECTION
from Tactics.punish import Punish
from Tactics.infinite import Infinite
from melee.enums import Character
from melee.enums import Stage

class Juggle(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)

    def canjuggle(smashbot_state, opponent_state, gamestate, framedata, difficulty):
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

        on_ground = opponent_state.on_ground or opponent_state.position.y < 1

        if self.logger:
            self.logger.log("Notes", "Predicted End Position: " + str(end_x) + " " + str(end_y) + " ", concat=True)
            self.logger.log("Notes", "on_ground: " + str(on_ground), concat=True)
            self.logger.log("Notes", "frames left: " + str(frames_left) + " ", concat=True)

        # Need to pivot the uptilt
        # Uptilt's hitbox is pretty forgiving if we do it a few frames early, so no big deal there
        if not on_ground:
            # If we can just throw out the attack and hit now, do it. No need to wait for them to fall further
            end_early_x, end_early_y = self.framedata.project_hit_location(opponent_state, 7)
            in_range = (abs(end_early_x - smashbot_state.position.x) < 8) and (abs(end_early_y - smashbot_state.position.y) < 12)
            if smashbot_state.action == Action.TURNING and in_range:
                self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                return

            if frames_left >= 9:
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return
            if (abs(smashbot_state.position.x - end_x) < 5) and (frames_left < 9):
                if 10 < smashbot_state.position.y - end_y < 15:
                    if smashbot_state.action == Action.TURNING:
                        self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                        return
                if smashbot_state.action == Action.DASHING:
                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return

        else:
            if self.framedata.is_roll(opponent_state.character, opponent_state.action):
                # We still have plenty of time, so just get closer to the DD spot
                #   Even if we're already close
                if frames_left > 10:
                    self.chain = None
                    self.pickchain(Chains.DashDance, [end_x])
                    return
                # We need to get to a position where our back is to the end position. We'll do a pivot stand to get there
                if (abs(smashbot_state.position.x - end_x) < 10):
                    # Pivot
                    if smashbot_state.action == Action.DASHING:
                        self.chain = None
                        self.pickchain(Chains.Run, [not smashbot_state.facing])
                        return
                    if smashbot_state.action in [Action.TURNING, Action.STANDING]:
                        if 7 <= frames_left <= 9:
                            if facing_away:
                                self.pickchain(Chains.Tilt, [TILT_DIRECTION.UP])
                                return
                            else:
                                # Can't grab a tech miss. Don't try
                                if opponent_state.action not in [Action.TECH_MISS_UP, Action.TECH_MISS_DOWN]:
                                    self.pickchain(Chains.GrabAndThrow, [THROW_DIRECTION.UP])
                                    return
                        if frames_left == 1:
                            self.pickchain(Chains.Waveshine)
                            return
                        else:
                            self.pickchain(Chains.Nothing)
                            return

                # We're further than 5 units away, so DD into their end position
                self.logger.log("Notes", "DD at: " + str(end_x), concat=True)
                self.chain = None
                self.pickchain(Chains.DashDance, [end_x])
                return

        self.logger.log("Notes", "Fall thru DD: " + str(end_x), concat=True)
        self.chain = None
        self.pickchain(Chains.DashDance, [end_x])
