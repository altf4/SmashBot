from strategies import strategy
from tactics import taunt

class Bait(strategy.Strategy):

    def picktactic(self):
        self.createtactic(taunt.Taunt)
        self.tactic.pickchain()
        return
