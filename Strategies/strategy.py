from abc import ABCMeta

class Strategy:
    __metaclass__ = ABCMeta
    tactic = None

    def picktactic(self, tactic, args=[]):
        if type(self.tactic) != tactic:
            self.tactic = tactic(*args)
        self.tactic.step()

    def step(self): ...
