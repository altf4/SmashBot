from abc import ABCMeta, abstractmethod

class Strategy:
    def __init__(self):
        self.tactic = None

    @abstractmethod
    def picktactic(self):
        pass

    def createtactic(self, new_tactic):
        if self.tactic == None:
            self.tactic = new_tactic()
        if type(self.tactic) !=  new_tactic:
            self.tactic = new_tactic()
