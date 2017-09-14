import melee
import globals
import Chains
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.smashattack import SMASH_DIRECTION
from Tactics.punish import Punish
from melee.enums import Character

class Infinite(Tactic):
    def __init__(self):
        self.movingright = globals.opponent_state.speed_x_attack + globals.opponent_state.speed_ground_x_self > 0

    def killpercent():
        character = globals.opponent_state.character
        if character == Character.CPTFALCON:
            return 113
        if character == Character.FALCO:
            return 93
        if character == Character.FOX:
            return 86
        if character == Character.SHEIK:
            return 92
        if character == Character.PIKACHU:
            return 73
        if character == Character.PEACH:
            return 80
        if character == Character.ZELDA:
            return 70
        if character == Character.MARTH:
            return 79
        if character == Character.JIGGLYPUFF:
            return 55
        return 120

    def caninfinite():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state
        isroll = globals.framedata.isroll(opponent_state.character, opponent_state.action)

        # Only infinite on difficulty 1, 2, and 3
        if globals.difficulty > 3:
            return False

        if opponent_state.action in [Action.SHIELD_START, Action.SHIELD, \
                Action.SHIELD_STUN, Action.SHIELD_REFLECT]:
            return False

        # Should we try a waveshine infinite?
        #   They need to have high friction and not fall down
        if opponent_state.action in [Action.STANDING, Action.TURNING, Action.DASHING, Action.RUNNING, \
                Action.WALK_SLOW, Action.WALK_MIDDLE, Action.WALK_FAST]:
            return False

        framesleft = Punish.framesleft()
        # This is off by one for hitstun
        framesleft -= 1

        # Give up the infinite if we're in our last dashing frame, and are getting close to the edge
        #   We are at risk of running off the edge when this happens
        if smashbot_state.action == Action.DASHING and smashbot_state.action_frame >= 11:
            if (smashbot_state.speed_ground_x_self > 0) == (smashbot_state.x > 0):
                edge_x = melee.stages.edgegroundposition(globals.gamestate.stage)
                if globals.opponent_state.x < 0:
                    edge_x = -edge_x
                edgedistance = abs(edge_x - globals.smashbot_state.x)
                if edgedistance < 16:
                    return False

        # If opponent is attacking, don't infinite
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            return False

        # If opponent is going to slide to the edge, then we have to stop
        endposition = opponent_state.x + globals.framedata.slidedistance(opponent_state, opponent_state.speed_x_attack, framesleft)
        if abs(endposition)+5 > melee.stages.edgegroundposition(globals.gamestate.stage):
            return False

        if globals.framedata.characterdata[opponent_state.character]["Friction"] >= 0.06 and \
                opponent_state.hitstun_frames_left > 1 and not isroll and opponent_state.on_ground \
                and opponent_state.percent < Infinite.killpercent():
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

        shinerange = 11.8
        if smashbot_state.action == Action.DASHING:
            shinerange = 9

        # Try to do the shine
        if globals.gamestate.distance < shinerange:
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

            # We always want to try to shine our opponent towards the center of the stage
            # If we are lined up right now, do the shine
            if smashbot_state.x < opponent_state.x < 0 or \
                    0 < opponent_state.x < smashbot_state.x:
                self.chain = None
                self.pickchain(Chains.Waveshine)
                return

            # If we are running away from our opponent, just shine now
            if (smashbot_state.speed_ground_x_self > 0) == onright:
                self.chain = None
                self.pickchain(Chains.Waveshine)
                return

        if smashbot_state.action == Action.LANDING_SPECIAL and smashbot_state.action_frame < 28:
            self.pickchain(Chains.Nothing)
            return
        self.pickchain(Chains.Run, [opponent_state.speed_x_attack > 0])
        return
