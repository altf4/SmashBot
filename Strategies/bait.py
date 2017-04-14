import melee
import globals
import Tactics
from Strategies.strategy import Strategy

class Bait(Strategy):
    def step(self):
        self.picktactic(Tactics.Punish)
