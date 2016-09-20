from tactics import tactic
from chains import multishine

class Taunt(tactic.Tactic):

    def pickchain(self):
        self.createtactic(multishine.MultiShine)
        self.chain.pressbuttons()
        return
