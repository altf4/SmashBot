from abc import ABCMeta

class Chain:
    __metaclass__ = ABCMeta
    interruptible = True

    def step(self): ...
