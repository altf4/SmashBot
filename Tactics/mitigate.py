import melee
import Chains
import random
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Chains.firefox import FIREFOX

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

        # For throws, randomize the TDI
        if smashbot_state.action in [Action.THROWN_FORWARD, Action.THROWN_BACK, Action.THROWN_DOWN, Action.THROWN_DOWN_2]:
            self.chain = None
            self.pickchain(Chains.DI, [random.choice([0, 0.5, 1]), random.choice([0, 0.5, 1])])
            return
        # Up throws are a little different. Don't DI up and down
        if smashbot_state.action == Action.THROWN_UP:
            self.chain = None
            self.pickchain(Chains.DI, [random.choice([0, 0.3, 0.5, 0.7, 1]), 0.5])
            return

        # Trajectory DI
        if smashbot_state.hitlag_left == 1:
            self.pickchain(Chains.TDI)
            return

        # Smash DI
        if smashbot_state.hitlag_left > 1:
            self.pickchain(Chains.SDI)
            return

        # Tech if we need to
        #   Calculate when we will land
        if smashbot_state.position.y > -4 and not smashbot_state.on_ground and \
                Action.DAMAGE_HIGH_1.value <= smashbot_state.action.value <= Action.DAMAGE_FLY_ROLL.value:
            framesuntillanding = 0
            speed = smashbot_state.speed_y_attack + smashbot_state.speed_y_self
            height = smashbot_state.position.y
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

        # Meteor cancel 8 frames after hitlag ended
        # TODO: keep track of Up-B lockout window.
        # TODO: Don't SDI an up input if we want to meteor cancel
        if smashbot_state.speed_y_attack < 0 and smashbot_state.action_frame == 8:
            if smashbot_state.jumps_left > 0:
                self.pickchain(Chains.Jump, [int(smashbot_state.position.x < 0)])
                return
            else:
                self.pickchain(Chains.Firefox, [FIREFOX.SAFERANDOM])
                return

        if smashbot_state.action == Action.TUMBLING:
            x = gamestate.frame % 2
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # DI randomly as a fallback
        self.pickchain(Chains.DI, [self.random_di, 0.5])
        return
