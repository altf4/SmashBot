import melee
import Chains
from Tactics.tactic import Tactic
from melee.enums import Character, Action

# Dash dance a just a little outside our opponont's range
class KeepDistance(Tactic):
    def _getbufferzone(self, opponent_state):
        character = opponent_state.character
        bufferzone = 30
        if character == Character.FOX:
            bufferzone = 18
        if character == Character.FALCO:
            bufferzone = 18
        if character == Character.CPTFALCON:
            bufferzone = 20
        if character == Character.MARTH:
            bufferzone = 30
        if character == Character.PIKACHU:
            bufferzone = 15
        if character == Character.JIGGLYPUFF:
            bufferzone = 15
        if character == Character.PEACH:
            bufferzone = 20
        if character == Character.ZELDA:
            bufferzone = 12
        if character == Character.SHEIK:
            bufferzone = 18
        if character == Character.SAMUS:
            bufferzone = 15

        # If we're in the first two difficulty levels, just get in there
        if self.difficulty > 2:
            bufferzone = 0
        # Stay a little further out if they're invulnerable
        if opponent_state.invulnerability_left > 0:
            bufferzone += 20

        # If opponent is in a dead fall, just get in there
        if opponent_state.action == Action.DEAD_FALL:
            bufferzone = 0

        return bufferzone

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        bufferzone = self._getbufferzone(opponent_state)
        #Don't dash RIGHT up against the edge. Leave a little space
        edgebuffer = 30
        # if we have our opponent cornered, reduce the edgebuffer
        edge = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.x < smashbot_state.x < 0 or \
                0 < smashbot_state.x < opponent_state.x:
            edgebuffer = 10

        # Figure out which side we should dash dance on
        #   If opponent is in the air, go behind them
        if not opponent_state.on_ground:
            if bufferzone == 0:
                bufferzone = 10
            if opponent_state.facing:
                bufferzone *= -1
        # If they're on the ground, stay on the side we're on
        else:
            onright = opponent_state.x < smashbot_state.x
            if not onright:
                bufferzone *= -1

        pivotpoint = opponent_state.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        self.chain = None
        self.pickchain(Chains.DashDance, [pivotpoint])
