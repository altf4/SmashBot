import melee
import globals
import Chains
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.smashattack import SMASH_DIRECTION
from Tactics.punish import Punish

class Infinite(Tactic):
    def __init__(self):
        self.movingright = globals.opponent_state.speed_x_attack + globals.opponent_state.speed_ground_x_self > 0

    def caninfinite():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        isroll = globals.framedata.isroll(opponent_state.character, opponent_state.action)

        # Only infinite on difficulty 1 and 2
        if globals.difficulty >= 3:
            return False

        # Should we try a waveshine infinite?
        #   They need to have high friction and not fall down
        if opponent_state.action in [Action.STANDING, Action.TURNING, Action.DASHING, Action.RUNNING]:
            return False

        framesleft = Punish.framesleft()
        # This is off by one for hitstun
        framesleft -= 1

        # If opponent is attacking, don't infinite
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            return False

        # If opponent is going to slide to the edge, then we have to stop
        endposition = opponent_state.x + globals.framedata.slidedistance(opponent_state.character, opponent_state.speed_x_attack, framesleft)
        if abs(endposition)+5 > melee.stages.edgegroundposition(globals.gamestate.stage):
            return False

        if globals.framedata.characterdata[opponent_state.character]["Friction"] >= 0.06 and \
                opponent_state.hitstun_frames_left > 1 and not isroll and opponent_state.on_ground \
                and opponent_state.percent < 120:
            return True

        return False

    def step(self):
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        framesleft = Punish.framesleft()
        # This is off by one for hitstun
        framesleft -= 1

        # Try to do the shine
        if globals.gamestate.distance < 11.8:
            # emergency backup shine
            if framesleft == 1:
                self.chain = None
                self.pickchain(Chains.Waveshine)
                return
            onright = opponent_state.x < smashbot_state.x
            opponentspeed = opponent_state.speed_x_attack + opponent_state.speed_ground_x_self
            # If opponent isn't moving, then just try to shine back towards the middle
            if abs(opponentspeed) > 0.01:
                self.movingright = opponentspeed > 0

            # We crossed them up!
            if onright == self.movingright:
                self.chain = None
                self.pickchain(Chains.Waveshine)
                return

        if smashbot_state.action == Action.LANDING_SPECIAL and smashbot_state.action_frame < 28:
            self.pickchain(Chains.Nothing)
            return
        self.pickchain(Chains.Run, [opponent_state.speed_x_attack > 0])
        return
