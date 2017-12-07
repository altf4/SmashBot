import melee
from Chains.chain import Chain

class Nothing(Chain):
    def step(self):
        self.controller.empty_input()
        self.interruptible = True
