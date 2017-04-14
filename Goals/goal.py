from abc import ABCMeta

class Goal:
    __metaclass__ = ABCMeta
    strat = None

    def pickstrategy(self, strat):
        if type(self.strat) != strat:
            self.strat = strat()
        self.strat.step()

    def step(self): ...
