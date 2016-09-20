from abc import ABCMeta, abstractmethod

class Chain:
    interruptible = True

    @abstractmethod
    def pressbuttons(self):
        pass
