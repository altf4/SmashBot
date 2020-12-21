import random
import melee
import Chains
from Tactics.tactic import Tactic
from melee.enums import Character, Action
from Chains.firefox import FIREFOX

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

        # Throw in a little randomness to fake out the opponent
        bufferzone += random.randint(-5, 5)

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

        for projectile in gamestate.projectiles:
            if self.logger:
                self.logger.log("Notes", "proj_x: " + str(projectile.position.x) + " ", concat=True)
                self.logger.log("Notes", "proj_y: " + str(projectile.position.y) + " ", concat=True)
                self.logger.log("Notes", "proj_x_speed: " + str(projectile.speed.x) + " ", concat=True)
                self.logger.log("Notes", "proj_y_speed: " + str(projectile.speed.y) + " ", concat=True)

        bufferzone = self._getbufferzone(opponent_state)
        #Don't dash RIGHT up against the edge. Leave a little space
        edgebuffer = 30
        # if we have our opponent cornered, reduce the edgebuffer
        edge = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.position.x < smashbot_state.position.x < 0 or \
                0 < smashbot_state.position.x < opponent_state.position.x:
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
            onright = opponent_state.position.x < smashbot_state.position.x
            if not onright:
                bufferzone *= -1

        pivotpoint = opponent_state.position.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        self.chain = None
        if not smashbot_state.off_stage:
            self.pickchain(Chains.DashDance, [pivotpoint])
        # If for whatever reason keepdistance gets called while Smashbot is recovering, it will do an emergency Firefox
        else:
            self.pickchain(Chains.Firefox)
