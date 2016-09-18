from abc import ABCMeta, abstractmethod

class Goal:
    def __init__(self):
        self.strategy = None

    @abstractmethod
    def pickstrategy(self):
        pass

    def createstrategy(self, new_strategy):
        if self.strategy == None:
            self.strategy = new_strategy()
        if type(self.strategy) !=  new_strategy:
            self.strategy = new_strategy()
