from abc import ABCMeta, abstractmethod

class Tactic:
    __metaclass__ = ABCMeta
    chain = None

    def pickchain(self, chain, args=[]):
        if type(self.chain) != chain:
            self.chain = chain(*args)
            self.chain.gamestate = self.gamestate
            self.chain.smashbot_state = self.smashbot_state
            self.chain.opponent_state = self.opponent_state
            self.chain.logger = self.logger
            self.chain.controller = self.controller
            self.chain.framedata = self.framedata
            self.chain.difficulty = self.difficulty
        self.chain.step()

    @abstractmethod
    def __init__(self, gamestate, smashbot_state, opponent_state, logger, controller, framedata, difficulty):
        self.gamestate = gamestate
        self.smashbot_state = smashbot_state
        self.opponent_state = opponent_state
        self.logger = logger
        self.controller = controller
        self.framedata = framedata
        self.difficulty = difficulty

    def step(self): ...

    def isinteruptible(self):
        if self.chain:
            return self.chain.interruptible
        else:
            return False
