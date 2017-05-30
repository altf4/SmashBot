from abc import ABCMeta

class Tactic:
    __metaclass__ = ABCMeta
    chain = None

    def pickchain(self, chain, args=[]):
        if type(self.chain) != chain:
            self.chain = chain(*args)
        self.chain.step()

    def step(self): ...

    def isinteruptible(self):
        if self.chain:
            return self.chain.interruptible
        else:
            return False
