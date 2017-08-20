import melee
import globals
import Chains
from melee.enums import Action, Button
from Tactics.tactic import Tactic

class Mitigate(Tactic):

    def needsmitigation():
        if Action.DAMAGE_AIR_1.value < globals.smashbot_state.action.value < Action.DAMAGE_FLY_ROLL.value:
            return True
        if globals.smashbot_state.action == Action.TUMBLING:
            return True

        return False

    def step(self):
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        smashbot_state = globals.smashbot_state

        # Smash DI
        if smashbot_state.hitlag_frames_left > 0:
            # Alternate each frame
            x = 0.5
            y = 0.5
            if bool(globals.gamestate.frame % 2):
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
        if Action.DAMAGE_AIR_1.value < smashbot_state.action.value < Action.DAMAGE_FLY_ROLL.value:
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
            x = globals.gamestate.frame % 2
            self.chain = None
            self.pickchain(Chains.DI, [x, 0.5])
            return

        # DI into the stage
        x = 0
        if smashbot_state.x < 0:
            x = 1
        self.chain = None
        self.pickchain(Chains.DI, [x, 0.5])
        return
