import melee
import globals
import Chains
import math
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Chains.dropdownshine import Dropdownshine

class Edgeguard(Tactic):

    # This is exactly flipped from the recover logic
    def canedgeguard():
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        if not smashbot_state.off_stage and opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return True

        if not opponent_state.off_stage:
            return False

        # We can now assume that opponent is off the stage...

        # If smashbot is on stage
        if not smashbot_state.off_stage:
            return True

        # If smashbot is in hitstun, then recover
        if smashbot_state.off_stage and smashbot_state.hitstun_frames_left > 0:
            return True

        # If smashbot is closer to the edge, edgeguard
        diff_x_opponent = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(opponent_state.x))
        diff_x = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        opponent_dist = math.sqrt( opponent_state.y**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( smashbot_state.y**2 + (diff_x)**2 )

        if smashbot_dist < opponent_dist:
            return True

        return False

    def step(self):
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        if Dropdownshine.inrange():
            self.pickchain(Chains.Dropdownshine)
            return

        if smashbot_state.action == Action.EDGE_CATCHING:
            self.pickchain(Chains.Nothing)
            return

        # How many frames will it take to get to our opponent right now?
        onedge = smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        # Stand up if opponent attacks us
        hitframe = globals.framedata.inrange(opponent_state, smashbot_state, globals.gamestate.stage)
        framesleft = hitframe - opponent_state.action_frame
        if hitframe != 0 and onedge and framesleft < 5:
            # Unless the attack is a grab, then don't bother
            if not globals.framedata.isgrab(opponent_state.character, opponent_state.action):
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return

        # Special exception for Fox/Falco illusion
        #   Since it is dumb and technically a projectile
        if opponent_state.character in [Character.FOX, Character.FALCO]:
            if opponent_state.action in [Action.SWORD_DANCE_2_MID]:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            if opponent_state.action in [Action.SWORD_DANCE_4_MID]:
                #TODO: Make this a chain
                self.chain = None
                globals.controller.press_button(Button.BUTTON_L)
                return

        # # Can we challenge their ledge?
        if not onedge and opponent_state.invulnerability_left < 5:
            self.pickchain(Chains.Grabedge)
            return

        # What recovery options does opponent have?
        # recoverlow # cross the stage line to recover
        # recoverhigh
        #
        # mustupb # they have to commit to an up-b to recover
        #
        # landonstage
        # grabedge

        #TODO How long will it take opponent to grab the edge?


        # Edgestall

        # Dash dance near the edge
        pivotpoint = opponent_state.x
        # Don't run off the stage though, adjust this back inwards a little if it's off
        edge = melee.stages.edgegroundposition(globals.gamestate.stage)
        edgebuffer = 10
        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        if smashbot_state.action == Action.EDGE_HANGING:
            self.chain = None
            self.pickchain(Chains.Nothing)
            return

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
