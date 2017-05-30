from abc import ABCMeta

class Goal:
    __metaclass__ = ABCMeta
    strat = None

    def pickstrategy(self, strat):
        if type(self.strat) != strat:
            self.strat = strat()
        self.strat.step()

    def step(self): ...

    def __str__(self):
        string = ""
        if not self.strat:
            return string
        string += str(type(self.strat))

        if not self.strat.tactic:
            return string
        string += str(type(self.strat.tactic))

        if not self.strat.tactic.chain:
            return string
        string += str(type(self.strat.tactic.chain))
        return string
