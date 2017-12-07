from abc import ABCMeta

class Strategy:
    __metaclass__ = ABCMeta
    tactic = None

    def picktactic(self, tactic):
        if type(self.tactic) != tactic:
            self.tactic = tactic(self.gamestate,
                                self.smashbot_state,
                                self.opponent_state,
                                self.logger,
                                self.controller,
                                self.framedata,
                                self.difficulty
            )
        self.tactic.step()

    def step(self): ...
