import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class SD(Chain):
    def step(self, gamestate, smashbot_state, opponent_state):
        self.interruptible = True

        if smashbot_state.action in [Action.FALLING, Action.ON_HALO_WAIT]:
            self.controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            return

        landingactionable = smashbot_state.action == Action.LANDING and smashbot_state.action_frame > 4
        if smashbot_state.action in [Action.WALK_SLOW, Action.WALK_MIDDLE, Action.WALK_FAST, Action.CROUCH_START, Action.CROUCHING, Action.LANDING_SPECIAL] or landingactionable:
                self.controller.empty_input()
                return

        onright = smashbot_state.x > 0
        if onright:
            self.controller.tilt_analog(Button.BUTTON_MAIN, 1, 0.5)
        else:
            self.controller.tilt_analog(Button.BUTTON_MAIN, 0, 0.5)
