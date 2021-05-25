import melee
import Chains
from melee.enums import Action, Character
from Tactics.tactic import Tactic

class Retreat(Tactic):
    def shouldretreat(smashbot_state, opponent_state, gamestate, camp):
        if smashbot_state.invulnerability_left > 1:
            return False

        shieldactions = [Action.SHIELD_START, Action.SHIELD, Action.SHIELD_RELEASE, \
            Action.SHIELD_STUN, Action.SHIELD_REFLECT]

        losing = smashbot_state.stock < opponent_state.stock
        if smashbot_state.stock == opponent_state.stock:
            losing = smashbot_state.percent > opponent_state.percent

        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            # If we're losing, don't retreat
            if not losing:
                return True

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW] \
            and opponent_state.character in [Character.FOX, Character.FALCO]
        if firefox:
            return True

        # If opponent is landing from an attack, and we're sheilding, retreat!
        if opponent_state.action in [Action.DAIR_LANDING, Action.NAIR_LANDING, Action.FAIR_LANDING, \
                Action.UAIR_LANDING, Action.BAIR_LANDING, Action.LANDING] and smashbot_state.action in shieldactions:
            return True

        # If opponent is falling, and we're in shield, retreat
        if opponent_state.speed_y_self < 0 and not opponent_state.on_ground and smashbot_state.action in shieldactions:
            return True

        # If there's a Samus bomb between us and opponent
        for projectile in gamestate.projectiles:
            if projectile.type == melee.enums.ProjectileType.SAMUS_BOMB:
                if smashbot_state.position.x < projectile.x < opponent_state.position.x or smashbot_state.position.x > projectile.x > opponent_state.position.x:
                    return True
                if opponent_state.position.y > 10:
                    return True

        return False

    def is_rapid_jab(opponent_state):
        if opponent_state.action == Action.LOOPING_ATTACK_MIDDLE:
            return True
        if opponent_state.character == Character.PIKACHU and opponent_state.action == Action.NEUTRAL_ATTACK_1:
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
            self.pickchain(Chains.Wavedash, [1, False])
            return

        bufferzone = 30
        if opponent_state.character == Character.SHEIK and opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            bufferzone = 55

        # Samus bomb?
        samus_bomb = False
        for projectile in gamestate.projectiles:
            if projectile.type == melee.enums.ProjectileType.SAMUS_BOMB:
                if smashbot_state.position.x < projectile.x < opponent_state.position.x or smashbot_state.position.x > projectile.x > opponent_state.position.x:
                    samus_bomb = True
        if samus_bomb:
            bufferzone = 60
        if opponent_state.action == Action.LOOPING_ATTACK_MIDDLE:
            bufferzone += 15

        onright = opponent_state.position.x < smashbot_state.position.x
        if not onright:
            bufferzone *= -1

        if Retreat.is_rapid_jab(opponent_state):
            bufferzone = 60

        pivotpoint = opponent_state.position.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        edgebuffer = 10
        edge = melee.stages.EDGE_GROUND_POSITION[gamestate.stage] - edgebuffer
        # If we are about to pivot near the edge, just grab the edge instead
        if abs(pivotpoint) > edge and opponent_state.position.y < 20:
            self.pickchain(Chains.Grabedge)
            return

        pivotpoint = min(pivotpoint, edge)
        pivotpoint = max(pivotpoint, -edge)

        # TODO make this a general function for all projectiles
        missle_approaching = False
        for projectile in gamestate.projectiles:
            if projectile.type in [melee.ProjectileType.SAMUS_MISSLE, melee.ProjectileType.SAMUS_CHARGE_BEAM]:
                missle_approaching = True

        # Only do this laser if we are on the same level as the opponent
        if abs(opponent_state.position.y - smashbot_state.position.y) < 5 and not missle_approaching:
            if samus_bomb and opponent_state.action == Action.SWORD_DANCE_4_MID and opponent_state.action_frame < 10:
                self.pickchain(Chains.Laser)
                return

        # If opponent is on a side platform, board the opposite platform and laser
        #   They don't need to be standing on the plat, just sort of shortly above it
        side_plat_height, side_plat_left, side_plat_right = melee.side_platform_position(opponent_state.position.x > 0, gamestate.stage)
        other_side_plat_height, other_side_plat_left, other_side_plat_right = melee.side_platform_position(opponent_state.position.x < 0, gamestate.stage)
        if (side_plat_height is not None) and (opponent_state.position.y+1 > side_plat_height) and (side_plat_left < opponent_state.position.x < side_plat_right):
            # If we're already on the platform
            if smashbot_state.position.y > 5 and smashbot_state.on_ground:
                # Make sure we're in the center-ish of the platform
                if (other_side_plat_left+5 < smashbot_state.position.x < other_side_plat_right-5) and not missle_approaching:
                    self.pickchain(Chains.Laser)
                    return
                else:
                    self.chain = None
                    self.pickchain(Chains.DashDance, [other_side_plat_left + (other_side_plat_right - other_side_plat_left / 2)])
                    return
            else:
                self.pickchain(Chains.BoardSidePlatform, [opponent_state.position.x < 0])
                return

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
