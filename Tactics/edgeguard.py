import melee
import globals
import Chains
from melee.enums import Action, Button
from Tactics.tactic import Tactic
from Chains.dropdownshine import Dropdownshine

class Edgeguard(Tactic):

    # This is exactly flipped from the recover logic
    def canedgeguard():
        if not globals.smashbot_state.off_stage and globals.opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return True

        if not globals.opponent_state.off_stage:
            return False

        # We can now assume that we're off the stage...

        # If opponent is on stage
        if not globals.smashbot_state.off_stage:
            return True

        # If opponent is in hitstun, then recover
        if globals.smashbot_state.off_stage and globals.smashbot_state.hitstun_frames_left > 0:
            return True

        # If opponent is closer to the edge, recover
        if globals.smashbot_state.off_stage and (abs(globals.opponent_state.x) > abs(globals.smashbot_state.x)):
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

        # How many frames will it take to get to our opponent right now?

        # Can we armada shine?
        #   To do this, let's assume that we have to hit the opponent in the cooldown of an attack
        #   or in a laggy non-attack animation.
        # This means we have to hit them in the window of time between the last hitbox frame (if present)
        #   and the last unactionable frame of the action
        start = 1
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            start = globals.framedata.lasthitboxframe(opponent_state.character, opponent_state.action)

        end = globals.framedata.iasa(opponent_state.character, opponent_state.action)
        # -1 iasa means that it's not applicable. Instead, use the last frame of the animation
        if end == -1:
            end = globals.framedata.iasa(opponent_state.character, opponent_state.action)

        # Where will opponent end up when they're vulnerable?

        onedge = smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        if onedge and globals.framedata.isattack(opponent_state.character, opponent_state.action):
            self.chain = None
            self.pickchain(Chains.DI, [0.5, 0.65])
            return

        # Can we challenge their ledge?
        if opponent_state.invulnerability_left < 5:
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

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
