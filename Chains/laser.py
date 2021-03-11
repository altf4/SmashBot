import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class Laser(Chain):
    """Short-hop Double-laser in place"""
    def __init__(self):
        self.interruptible = True

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        # We can give up in the first few frames of landing
        if smashbot_state.action == Action.LANDING and smashbot_state.action_frame <= 3:
            self.interruptible = True
            controller.release_all()
            return

        # First get into position. We don't want to accidentally jump off the stage.
        #   In general, we just want to limit horizontal movement. So starting from pivot is fine
        if smashbot_state.action in [Action.TURNING, Action.STANDING, Action.LANDING]:
            self.interruptible = False
            if controller.prev.button[Button.BUTTON_Y]:
                controller.release_button(Button.BUTTON_Y)
            else:
                controller.press_button(Button.BUTTON_Y)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        # Short hop, so let go of jump when in knee bend
        if smashbot_state.action == Action.KNEE_BEND:
            self.interruptible = False
            controller.release_button(Button.BUTTON_Y)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        # Don't jump from a dash, the horizontal movement is too risky. Let's pivot-jump instead
        if smashbot_state.action == Action.DASHING:
            self.interruptible = True
            controller.release_button(Button.BUTTON_Y)
            controller.tilt_analog(Button.BUTTON_MAIN, int(not smashbot_state.facing), 0.5)
            return

        # Do a turnaround to make sure we're facing the opponent
        if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
            if smashbot_state.action_frame == 1:
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, int(smashbot_state.position.x < opponent_state.position.x), 0.5)
                controller.release_button(Button.BUTTON_B)
                return
            # Make sure we press B on frame 2 of jumping. Or else we won't double laser
            if smashbot_state.action_frame == 2:
                self.interruptible = False
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
                controller.press_button(Button.BUTTON_B)
                return

        # Spam B when in air
        if not smashbot_state.on_ground:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            if gamestate.frame % 2:
                controller.press_button(Button.BUTTON_B)
            else:
                controller.release_button(Button.BUTTON_B)
            return

        self.interruptible = True
        controller.release_all()
