from abc import ABCMeta, abstractmethod

class Tactic:
    def __init__(self):
        self.chain = None

    @abstractmethod
    def picktactic(self):
        pass

    def createtactic(self, new_chain):
        if self.chain == None:
            self.chain = new_chain()
        if type(self.chain) !=  new_chain:
            self.chain = new_chain()
