import melee
import globals
import Tactics
from Strategies.strategy import Strategy

class Sandbag(Strategy):
    def step(self):
        self.picktactic(Punish)
