import melee
import Chains
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Tactics.punish import Punish

class Approach(Tactic):
    def shouldapproach(smashbot_state, opponent_state, gamestate, framedata, logger):
        # Specify that this needs to be platform approach
        framesleft = Punish.framesleft(opponent_state, framedata, smashbot_state)
        if logger:
            logger.log("Notes", " framesleft: " + str(framesleft) + " ", concat=True)
        if framesleft >= 9:
            return True
        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        needswavedash = smashbot_state.action in [Action.DOWN_B_GROUND, Action.DOWN_B_STUN, \
            Action.DOWN_B_GROUND_START, Action.LANDING_SPECIAL, Action.SHIELD, Action.SHIELD_START, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        if needswavedash:
            self.pickchain(Chains.Wavedash)
            return

        # If opponent is on a side platform and we're not
        on_main_platform = smashbot_state.position.y < 1 and smashbot_state.on_ground
        if opponent_state.position.y > 1 and opponent_state.on_ground and on_main_platform and gamestate.stage != melee.enums.Stage.FOUNTAIN_OF_DREAMS:
            self.pickchain(Chains.BoardSidePlatform, [opponent_state.position.x > 0])
            return

        # If opponent is on top platform
        on_side_platform = (5 < smashbot_state.position.y < 35) and smashbot_state.on_ground
        top_platform_height, top_platform_left, top_platform_right = melee.top_platform_position(gamestate.stage)
        opp_top_platform = False
        if top_platform_height is not None:
            opp_top_platform = (opponent_state.position.y+1 >= top_platform_height) and (top_platform_left < opponent_state.position.x < top_platform_right)

        if on_side_platform and opp_top_platform:
            self.pickchain(Chains.BoardTopPlatform)
            return

        # Jump over Samus Bomb
        samus_bomb = opponent_state.character == Character.SAMUS and opponent_state.action == Action.SWORD_DANCE_4_MID
        # Falcon rapid jab
        falcon_rapid_jab = opponent_state.action == Action.LOOPING_ATTACK_MIDDLE
        # Are they facing the right way, though?
        facing_wrong_way = opponent_state.facing != (opponent_state.position.x < smashbot_state.position.x)

        if (samus_bomb or falcon_rapid_jab) and opponent_state.position.y < 5:
            landing_spot = opponent_state.position.x
            if opponent_state.position.x < smashbot_state.position.x:
                landing_spot -= 10
            else:
                landing_spot += 10

            # Don't jump off the stage
            if abs(landing_spot) < melee.stages.EDGE_GROUND_POSITION[gamestate.stage] and not facing_wrong_way:
                self.pickchain(Chains.JumpOver, [landing_spot])
                return

        self.chain = None
        self.pickchain(Chains.DashDance, [opponent_state.position.x])
