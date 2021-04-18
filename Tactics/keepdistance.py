import random
import melee
import Chains
from Tactics.tactic import Tactic
from melee.enums import Character, Action
from Chains.firefox import FIREFOX

# Dash dance a just a little outside our opponont's range
class KeepDistance(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        self.radius = 0
        self.stand_menacingly = False
        Tactic.__init__(self, logger, controller, framedata, difficulty)

    def _getbufferzone(self, opponent_state):
        character = opponent_state.character
        bufferzone = 30
        if character == Character.FOX:
            bufferzone = 25
        if character == Character.FALCO:
            bufferzone = 25
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

        # If oppoonent is attacking, keep a little further back to avoid running right into it
        if self.framedata.attack_state(opponent_state.character, opponent_state.action, opponent_state.action_frame) in [melee.enums.AttackState.ATTACKING, melee.enums.AttackState.WINDUP]:
            bufferzone += 20

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
        # Don't dash RIGHT up against the edge. Leave a little space
        edgebuffer = 30
        # if we have our opponent cornered, reduce the edgebuffer
        edge = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.position.x < smashbot_state.position.x < 0 or \
                0 < smashbot_state.position.x < opponent_state.position.x:
            edgebuffer = 10

        if opponent_state.position.x > smashbot_state.position.x:
            bufferzone *= -1

        pivotpoint = opponent_state.position.x + bufferzone
        # Don't run off the stage though, adjust this back inwards a little if it's off

        pivotpoint = min(pivotpoint, edge - edgebuffer)
        pivotpoint = max(pivotpoint, (-edge) + edgebuffer)

        if smashbot_state.action == Action.SHIELD_RELEASE:
            self.pickchain(Chains.Wavedash, [1.0, False])
            return

        # Switch up our dash dance radius every second
        if gamestate.frame % 60 == 0:
            self.radius = random.randint(0, 4)

        # Give ourselves a 1 in 30 chance of starting a "stand there menacingly" each pivot, if we're already in position
        if smashbot_state.action == Action.TURNING and (opponent_state.position.x < smashbot_state.position.x) == smashbot_state.facing:
            if (random.randint(0, 30) == 0):
                self.stand_menacingly = True

        if self.framedata.is_attack(opponent_state.character, opponent_state.action) or abs(pivotpoint - smashbot_state.position.x) > 10:
                self.stand_menacingly = False

        if self.stand_menacingly:
            self.pickchain(Chains.Nothing)
            return

        self.chain = None
        if not smashbot_state.off_stage:
            self.pickchain(Chains.DashDance, [pivotpoint, self.radius])
        # If for whatever reason keepdistance gets called while Smashbot is recovering, it will do an emergency Firefox
        else:
            self.pickchain(Chains.Firefox)
