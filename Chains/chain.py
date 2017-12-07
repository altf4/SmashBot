from abc import ABCMeta

class Chain:
    __metaclass__ = ABCMeta
    interruptible = True
    gamestate = None
    smashbot_state = None
    opponent_state = None
    logger = None
    controller = None
    framedata = None
    difficulty = None

    def step(self): ...
