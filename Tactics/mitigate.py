import melee
import Chains
import random
from melee.enums import Action, Button
from Tactics.tactic import Tactic
from melee.enums import Character

class Mitigate(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        self.random_di = random.randint(0, 1)

    def needsmitigation(smashbot_state):
        # Always interrupt if we got hit. Whatever chain we were in will have been broken anyway
        if smashbot_state.action in [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, \
                Action.GRAB_PUMMELED, Action.GRAB_PULLING_HIGH, Action.GRABBED_WAIT_HIGH, Action.PUMMELED_HIGH]:
            return True

        # Thrown action
        if smashbot_state.action in [Action.THROWN_FORWARD, Action.THROWN_BACK, \
                Action.THROWN_UP, Action.THROWN_DOWN, Action.THROWN_DOWN_2]:
            return True

        if smashbot_state.hitstun_frames_left == 0:
            return False

        if Action.DAMAGE_HIGH_1.value <= smashbot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            return True
        if smashbot_state.action == Action.TUMBLING:
            return True

        return False

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        # Did we get grabbed?
        if smashbot_state.action in [Action.GRABBED, Action.GRAB_PUMMELED, Action.GRAB_PULL, \
                Action.GRAB_PUMMELED, Action.GRAB_PULLING_HIGH, Action.GRABBED_WAIT_HIGH, Action.PUMMELED_HIGH]:
            self.pickchain(Chains.Struggle)
            return

        # Smash DI
        if smashbot_state.hitlag > 0:
            # Alternate each frame
            x = 0.5
            y = 0.5
            cx = 0.5
            cy = 0.5
            if not (opponent_state.character in [Character.PEACH, Character.PIKACHU, Character.SAMUS, Character.SHEIK] and opponent_state.action == Action.DOWNSMASH):
                cy = 0
            if bool(gamestate.frame % 2):
                # If we're off the stage, DI up and in
                if smashbot_state.off_stage:
                    y = 1
                    x = 0
                    if smashbot_state.x < 0:
                        x = 1
                else:
                    if smashbot_state.percent > 60:
                        y = 1
                        x = 0
                        if smashbot_state.x < 0:
                            x = 1
                    # If at low damage, DI away
                    else:
                        y = 0.5
                        x = 1
                        if smashbot_state.x < 0:
                            x = 0
            self.chain = None
            self.pickchain(Chains.DI, [x, y, cx, cy])
            return

        # Tech if we need to
        #   Calculate when we will land
        if smashbot_state.y > -4 and not smashbot_state.on_ground and \
                Action.DAMAGE_HIGH_1.value <= smashbot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            framesuntillanding = 0
            speed = smashbot_state.speed_y_attack + smashbot_state.speed_y_self
            height = smashbot_state.y
            gravity = self.framedata.characterdata[smashbot_state.character]["Gravity"]
            termvelocity = self.framedata.characterdata[smashbot_state.character]["TerminalVelocity"]
            while height > 0:
                height += speed
                speed -= gravity
                speed = max(speed, -termvelocity)
                framesuntillanding += 1
                # Shortcut if we get too far
                if framesuntillanding > 120:
                    break
            # Do the tech
            if framesuntillanding < 4:
                self.pickchain(Chains.Tech)
                return

        # Regular DI
        if Action.DAMAGE_HIGH_1.value <= smashbot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            # DI up and in if we're at high percent
            x = 0.5
            y = 0.5
            if smashbot_state.percent > 60:
                y = 1
                x = 0
                if smashbot_state.x < 0:
                    x = 1
            # If at low damage, DI away
            else:
                y = 0.5
                x = 1
                if smashbot_state.x < 0:
                    x = 0
            self.chain = None
            self.pickchain(Chains.DI, [x, y])
            return
        if smashbot_state.action == Action.TUMBLING:
            x = gamestate.frame % 2
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # DI randomly as a fallback
        self.pickchain(Chains.DI, [self.random_di, 0.5])
        return
