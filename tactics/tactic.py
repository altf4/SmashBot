from abc import ABCMeta, abstractmethod

class Tactic:
    def __init__(self):
        pass

    @abstractmethod
    def pickchain(self):
        pass
