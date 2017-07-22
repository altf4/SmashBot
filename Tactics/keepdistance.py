import melee
import globals
import Chains
from Tactics.tactic import Tactic
from melee.enums import Character

# Dash dance a just a little outside our opponont's range
class KeepDistance(Tactic):
    def getbufferzone(self):
        character = globals.opponent_state.character
        if character == Character.FOX:
            return 20
        if character == Character.FALCO:
            return 20
        if character == Character.CPTFALCON:
            return 20
        if character == Character.MARTH:
            return 30
        return 30

    def step(self):
        opponent_state = globals.opponent_state
        smashbot_state = globals.smashbot_state

        bufferzone = self.getbufferzone()
        #Don't dash RIGHT up against the edge. Leave a little space
        edgebuffer = 30
        # Figure out which side we should dash dance on
        # (the side we're on)
        onright = opponent_state.x < smashbot_state.x
        if not onright:
            bufferzone *= -1

        pivotpoint = opponent_state.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        edge = melee.stages.edgegroundposition(globals.gamestate.stage)
        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
