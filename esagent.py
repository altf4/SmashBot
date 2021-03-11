import melee
import math
from Strategies.bait import Bait

from melee.enums import ProjectileSubtype, Action

class ESAgent():
    """
    Expert system agent for SmashBot.
    This is the "manually programmed" TAS-looking agent.
    """
    def __init__(self, dolphin, smashbot_port, opponent_port, controller, difficulty=4):
        self.smashbot_port = smashbot_port
        self.opponent_port = opponent_port
        self.controller = controller
        self.framedata = melee.framedata.FrameData()
        self.logger = dolphin.logger
        self.difficulty = difficulty
        self.ledge_grab_count = 0
        self.strategy = Bait(self.logger,
                            self.controller,
                            self.framedata,
                            self.difficulty)

    def act(self, gamestate):
        knownprojectiles = []
        for projectile in gamestate.projectiles:
            if projectile.subtype not in [ProjectileSubtype.UNKNOWN_PROJECTILE, ProjectileSubtype.PEACH_PARASOL]:
                knownprojectiles.append(projectile)
        gamestate.projectiles = knownprojectiles

        # Keep a ledge grab count
        if gamestate.player[self.opponent_port].action == Action.EDGE_CATCHING and gamestate.player[self.opponent_port].action_frame == 1:
            self.ledge_grab_count += 1
        if gamestate.player[self.opponent_port].on_ground:
            self.ledge_grab_count = 0
        if gamestate.frame == -123:
            self.ledge_grab_count = 0
        gamestate.custom["ledge_grab_count"] = self.ledge_grab_count

        self.strategy.step(gamestate,
                           gamestate.players[self.smashbot_port],
                           gamestate.players[self.opponent_port])
