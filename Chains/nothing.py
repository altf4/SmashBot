import melee
from Chains.chain import Chain

class Nothing(Chain):
    def step(self, gamestate, smashbot_state, opponent_state):
        self.controller.empty_input()
        self.interruptible = True
