from abc import ABCMeta, abstractmethod

class Strategy:
    def __init__(self):
        pass

    @abstractmethod
    def picktactic(self):
        pass
