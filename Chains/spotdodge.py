import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class SpotDodge(Chain):
    def step(self):
        controller = self.controller
        smashbot_state = self.smashbot_state

        # Don't try to spot dodge in the air
        if not smashbot_state.on_ground:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're shielding, do the spot dodge
        if smashbot_state.action == Action.SHIELD_REFLECT:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            return

        # Let go once we're in the spotdodge
        if smashbot_state.action == Action.SPOTDODGE:
            self.interruptible = True
            controller.empty_input()
            return

        # If we already pressed L last frame, let go
        if controller.prev.button[Button.BUTTON_L]:
            self.interruptible = True
            controller.empty_input()
            return

        self.interruptible = False
        controller.press_button(Button.BUTTON_L)
        controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)
