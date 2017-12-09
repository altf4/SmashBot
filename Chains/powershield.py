import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

class Powershield(Chain):
    def __init__(self, hold=False):
        self.hold = hold

    def step(self):
        controller = self.controller
        smashbot_state = self.smashbot_state
        opponent_state = self.opponent_state

        # Don't try to shield in the air
        if not smashbot_state.on_ground:
            self.interruptible = True
            controller.empty_input()
            return

        # FireFox is different
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID] and opponent_state.character in [Character.FOX, Character.FALCO]

        # If we get to cooldown, let go
        attackstate = self.framedata.attackstate_simple(self.opponent_state)
        if attackstate in [melee.enums.AttackState.COOLDOWN, melee.enums.AttackState.NOT_ATTACKING] \
                and len(self.gamestate.projectiles) == 0 and not firefox:
            self.interruptible = True
            controller.empty_input()
            return

        # Hold onto the shield until the attack is done
        # TODO: Shield DI in here
        if self.hold:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            controller.press_button(Button.BUTTON_L)
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
            controller.press_button(Button.BUTTON_L)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        self.interruptible = True
        controller.empty_input()
