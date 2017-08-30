import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

class Powershield(Chain):
    def __init__(self, hold=False):
        self.hold = hold

    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state

        # Don't try to shield in the air
        if not smashbot_state.on_ground:
            self.interruptible = True
            controller.empty_input()
            return

        # If we get to cooldown, let go
        attackstate = globals.framedata.attackstate_simple(globals.opponent_state)
        if attackstate in [melee.enums.AttackState.COOLDOWN, melee.enums.AttackState.NOT_ATTACKING] \
                and len(globals.gamestate.projectiles) == 0:
            self.interruptible = True
            controller.empty_input()
            return

        # Hold onto the shield until the attack is done
        # TODO: Shield DI in here
        if self.hold:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            controller.press_button(Button.BUTTON_L);
            return

        # We're done if we are in shield release
        if smashbot_state.action == Action.SHIELD_RELEASE:
            self.interruptible = True
            controller.empty_input()
            return

        isshielding = smashbot_state.action == Action.SHIELD \
            or smashbot_state.action == Action.SHIELD_START \
            or smashbot_state.action == Action.SHIELD_REFLECT \
            or smashbot_state.action == Action.SHIELD_STUN \
            or smashbot_state.action == Action.SHIELD_RELEASE

        # If we're in shield stun, we can let go
        if smashbot_state.action == Action.SHIELD_STUN:
            self.interruptible = True
            controller.empty_input()
            return

        # If we already pressed L last frame, let go
        if controller.prev.button[Button.BUTTON_L]:
            controller.empty_input()
            return

        if not isshielding:
            self.interruptible = False
            controller.press_button(Button.BUTTON_L);
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        self.interruptible = True
        controller.empty_input()
