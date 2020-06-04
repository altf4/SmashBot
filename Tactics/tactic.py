from abc import ABCMeta, abstractmethod

class Tactic:
    __metaclass__ = ABCMeta
    chain = None

    def pickchain(self, chain, args=[]):
        if type(self.chain) != chain:
            self.chain = chain(*args)
            self.chain.logger = self.logger
            self.chain.controller = self.controller
            self.chain.framedata = self.framedata
            self.chain.difficulty = self.difficulty
        self.chain.step(self._propagate[0], self._propagate[1], self._propagate[2])

    @abstractmethod
    def __init__(self, logger, controller, framedata, difficulty):
        self.logger = logger
        self.controller = controller
        self.framedata = framedata
        self.difficulty = difficulty

    def step(self, gamestate, smashbot_state, opponent_state): ...

    def isinteruptible(self):
        if self.chain:
            return self.chain.interruptible
        else:
            return False
