import melee
import globals
import Chains
import math
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic

class Defend(Tactic):
    def needsprojectiledefense():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        projectiles = globals.gamestate.projectiles

        # Ignore Fox lasers. They 'just' do damage. Nothing we actually care about
        #   It's worse to put ourselves in stun just to prevent a few percent
        if smashbot_state.character == Character.FOX:
            return False

        # Loop through each projectile
        for projectile in projectiles:
            size = 10
            if projectile.subtype == melee.enums.ProjectileSubtype.PIKACHU_THUNDERJOLT_1:
                size = 18
            if projectile.subtype == melee.enums.ProjectileSubtype.NEEDLE_THROWN:
                size = 12

            # Is this about to hit us in the next frame?
            proj_x, proj_y = projectile.x, projectile.y
            for i in range(0, 1):
                proj_x += projectile.x_speed
                proj_y += projectile.y_speed
                smashbot_y = smashbot_state.y
                smashbot_x = smashbot_state.x + smashbot_state.speed_ground_x_self
                # This is a bit hacky, but it's easiest to move our "center" up a little for the math
                if smashbot_state.on_ground:
                    smashbot_y += 8
                distance = math.sqrt((proj_x - smashbot_x)**2 + (proj_y - smashbot_y)**2)

                if distance < size:
                    return True
        return False

    def needsdefense():
        # Is opponent attacking?
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        framedata = globals.framedata

        # What state of the attack is the opponent in?
        # Windup / Attacking / Cooldown / Not Attacking
        attackstate = framedata.attackstate_simple(opponent_state)
        if attackstate == melee.enums.AttackState.COOLDOWN:
            return False
        if attackstate == melee.enums.AttackState.NOT_ATTACKING:
            return False

        # Will we be hit by this attack if we stand still?
        hitframe = framedata.inrange(opponent_state, smashbot_state, globals.gamestate.stage)
        if hitframe:
            return True

        return False

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        projectiles = globals.gamestate.projectiles
        framedata = globals.framedata

        # Do we need to defend against a projectile?
        #   If there is a projectile, just assume that's why we're here.
        #   TODO: maybe we should re-calculate if this is what we're defending
        if projectiles:
            if smashbot_state.action == Action.EDGE_HANGING:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            self.pickchain(Chains.Powershield)
            return

        # Is the attack a grab? If so, spot dodge right away
        if opponent_state.action == Action.GRAB or \
            opponent_state.action == Action.GRAB_RUNNING:
            self.pickchain(Chains.SpotDodge)
            return

        hitframe = framedata.inrange(opponent_state, smashbot_state, globals.gamestate.stage)
        framesuntilhit = hitframe - opponent_state.action_frame

        if globals.logger:
            globals.logger.log("Notes", "framesuntilhit: " + str(framesuntilhit) + " ", concat=True)

        # If the attack has exactly one hitbox, then try shine clanking to defend
        if framedata.hitboxcount(opponent_state.character, opponent_state.action) == 1:
            # It must be the first frame of the attack
            firstframe = framedata.firsthitboxframe(opponent_state.character, opponent_state.action)
            if hitframe == firstframe:
                # For the time being, let's restrict this to ground attacks only
                if opponent_state.on_ground:
                    if (framesuntilhit == 2 and smashbot_state.action == Action.DASHING) or \
                            (framesuntilhit == 1 and smashbot_state.action == Action.TURNING):
                        self.pickchain(Chains.Waveshine)
                        return

        # Are we in the powershield window?
        if framesuntilhit <= 2:
            if smashbot_state.action == Action.EDGE_HANGING:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            hold = framedata.hitboxcount(opponent_state.character, opponent_state.action) > 1
            self.pickchain(Chains.Powershield, [hold])
        else:
            bufferzone = 35
            pivotpoint = opponent_state.x
            # Dash to a point away from the opponent, out of range
            if opponent_state.x < smashbot_state.x:
                # Dash right
                pivotpoint += bufferzone
                # But don't run off the edge
                pivotpoint = min(melee.stages.edgegroundposition(globals.gamestate.stage)-5, pivotpoint)
            else:
                # Dash Left
                pivotpoint -= bufferzone
                # But don't run off the edge
                pivotpoint = max(-melee.stages.edgegroundposition(globals.gamestate.stage) + 5, pivotpoint)
            self.pickchain(Chains.DashDance, [pivotpoint])
