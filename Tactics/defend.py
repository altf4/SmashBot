import melee
import globals
import Chains
import math
from melee.enums import Action, Button
from Tactics.tactic import Tactic

class Defend(Tactic):
    def needsprojectiledefense():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        projectiles = globals.gamestate.projectiles
        # Loop through each projectile
        for projectile in projectiles:
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
                # TODO: Make this distance dependent on the projectile subtype
                if distance < 10:
                    return True
        return False

    def needsdefense():
        # Is opponent attacking?
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            # What state of the attack is the opponent in?
            # Windup / Attacking / Cooldown
            attackstate = globals.framedata.attackstate_simple(opponent_state)
            if attackstate == melee.enums.AttackState.WINDUP:
                # 1: Sweep out predicted attack zone. Do we need to care about the attack?
                #   break
                # IE: Maybe the attack is the wrong way or too far away
                #TODO

                # 2: Can we hit them first before their hitbox comes out?
                #   Punish
                # Already handled above

                # 3: Can we run away from the hit so that it whiffs?
                #   Defend

                # 4: Shield or spotdodge the attack
                #   Defend
                return True

            if attackstate == melee.enums.AttackState.ATTACKING:
                return True

            if attackstate == melee.enums.AttackState.COOLDOWN:
                pass
        return False

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        projectiles = globals.gamestate.projectiles

        # Do we need to defend against a projectile?
        #   If there is a projectile, just assume that's why we're here.
        #   TODO: maybe we should re-calculate if this is what we're defending
        if projectiles:
            self.pickchain(Chains.Powershield)
            return

        grabbedactions = [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, Action.GRAB_PUMMELED]
        if smashbot_state.action in grabbedactions:
            self.pickchain(Chains.Struggle)
            return

        # Is the attack a grab? If so, spot dodge right away
        if opponent_state.action == Action.GRAB or \
            opponent_state.action == Action.GRAB_RUNNING:
            self.pickchain(Chains.SpotDodge)
            return

        # If the hitbox is next frame, do something about it
        firsthitbox = globals.framedata.firsthitboxframe(opponent_state.character, \
            opponent_state.action)
        framesuntilhit = firsthitbox - opponent_state.action_frame

        # Do we only have one frame left?
        if framesuntilhit == 1:
            self.pickchain(Chains.Powershield)
        else:
            # Just dash at the opponent I guess
            self.pickchain(Chains.DashDance, [opponent_state.x])
