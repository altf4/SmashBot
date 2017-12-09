import melee
from Strategies.bait import Bait

"""
Expert system agent for SmashBot.
This is the "manually programmed" TAS-looking agent.
Only plays Fox on FD.
"""
class ESAgent():
    def __init__(self, dolphin, gamestate, smashbot_port, opponent_port):
        self.gamestate = gamestate
        self.controller = melee.controller.Controller(port=smashbot_port, dolphin=dolphin)
        self.smashbot_state = self.gamestate.player[smashbot_port]
        self.opponent_state = self.gamestate.player[opponent_port]
        self.framedata = melee.framedata.FrameData()
        self.logger = dolphin.logger
        self.difficulty = 4
        self.strategy = Bait(self.gamestate,
                            self.smashbot_state,
                            self.opponent_state,
                            self.logger,
                            self.controller,
                            self.framedata,
                            self.difficulty)

    def act(self):
        self.strategy.step()
