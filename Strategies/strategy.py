from abc import ABCMeta

class Strategy:
    __metaclass__ = ABCMeta
    tactic = None

    def picktactic(self, tactic):
        if type(self.tactic) != tactic:
            self.tactic = tactic(self.logger,
                                self.controller,
                                self.framedata,
                                self.difficulty
            )
        self.tactic.step(self._propagate[0], self._propagate[1], self._propagate[2])

    def step(self, gamestate, smashbot_state, opponent_state): ...
