import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

class JumpOver(Chain):
    """Short-hop Double-laser in place"""
    def __init__(self, landing_spot):
        self.interruptible = True
        self.landing_spot = landing_spot

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        if self.logger:
            self.logger.log("Notes", " landing_spot: " + str(self.landing_spot) + " ", concat=True)

        controller.release_button(Button.BUTTON_L)
        # We can give up in the first few frames of landing
        if smashbot_state.action == Action.LANDING and smashbot_state.action_frame <= 3:
            self.interruptible = True
            controller.release_all()
            return

        landing_direction = smashbot_state.position.x < self.landing_spot

        starting_distance = 45
        if opponent_state.character in [Character.FALCO, Character.FOX]:
            starting_distance = 40

        # If we're in position to do the jump, do it
        if smashbot_state.action in [Action.DASHING, Action.RUNNING]:
            if abs(smashbot_state.position.x - self.landing_spot) < starting_distance:
                if smashbot_state.facing == landing_direction:
                    self.interruptible = False
                    if controller.prev.button[Button.BUTTON_Y]:
                        controller.release_button(Button.BUTTON_Y)
                    else:
                        controller.press_button(Button.BUTTON_Y)
                    controller.tilt_analog(Button.BUTTON_MAIN, int(landing_direction), 0.5)
                    return

        # Full hop, so hold onto the Y button
        if smashbot_state.action == Action.KNEE_BEND:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            return

        # Otherwise, dash/drift at the landing spot
        if smashbot_state.on_ground:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, int(landing_direction), 0.5)
            return
        else:
            self.interruptible = False
            controller.release_button(Button.BUTTON_Y)
            fastfall = 0.5
            if smashbot_state.speed_y_self < 0:
                fastfall = 0
            controller.tilt_analog(Button.BUTTON_MAIN, int(landing_direction), fastfall)
            return
