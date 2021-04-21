import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class AIR_ATTACK_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2
    BACK = 3
    NEUTRAL = 4

class AirAttack(Chain):
    def __init__(self, target_x, target_y, height_level, direction=AIR_ATTACK_DIRECTION.DOWN):
        self.direction = direction
        self.target_x = target_x
        self.target_y = target_y
        self.height_level = height_level

    def frame_commitment(height_level):
        """Given the target height level, how many frames worth of commitment does it require?"""
        if height_level == 2:
            return 25 # Higher because we need to drop-down upair
        if height_level == 3:
            return 15
        if height_level == 4:
            return 19
        if height_level == 5:
            return 23
        if height_level == 6:
            return 29
        return 500

    def height_levels():
        """Returns a list of the possible attack height levels"""
        return [2, 3, 4, 5, 6]

    def attack_height(height_level):
        """For a given height level, returns the height of our attack"""
        if height_level == 2:
            return 20
        if height_level == 3:
            return 31
        if height_level == 4:
            return 43
        if height_level == 5:
            return 55
        if height_level == 6:
            return 66
        return 500

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        # Landing / falling. We're done
        if smashbot_state.action in [Action.LANDING, Action.UAIR_LANDING, Action.FALLING]:
            self.interruptible = True
            controller.release_all()
            return

        # We've somehow fallen off stage
        if smashbot_state.position.y < 0:
            self.interruptible = True
            controller.release_all()
            return

        # Full hop
        if smashbot_state.on_ground:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
            if controller.prev.button[Button.BUTTON_Y] and smashbot_state.action != Action.KNEE_BEND:
                controller.release_button(Button.BUTTON_Y)
                return
            else:
                controller.press_button(Button.BUTTON_Y)
                # Only jump to the side if we're far away horizontally. If they're right above, then just straight up and drift
                x = int(self.target_x > smashbot_state.position.x)
                if abs(self.target_x - smashbot_state.position.x) < 10:
                    x = 0.5
                controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
                return

        # falling back down
        if smashbot_state.speed_y_self < 0:
            # L-Cancel
            #   Spam shoulder button
            if controller.prev.l_shoulder == 0:
                controller.press_shoulder(Button.BUTTON_L, 1.0)
            else:
                controller.press_shoulder(Button.BUTTON_L, 0)

            # Drift onto stage if we're near the edge
            if abs(smashbot_state.position.x) + 10 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage]:
                controller.tilt_analog(Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), 0)
                return
            else:
                # fastfall
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0)
                return

        # Height level 2 is a bit different, handle it special
        if self.height_level == 2:
            # Up-air on frame 11
            if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD] and smashbot_state.action_frame >= 11:
                controller.tilt_analog(Button.BUTTON_C, 0.5, 1)
                return
            if smashbot_state.action in [Action.UAIR, Action.BAIR, Action.DAIR, Action.FAIR, Action.NAIR]:
                # Fast fall on frame 8
                if smashbot_state.action_frame >= 8:
                    controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0)
                    return

            controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
            return

        # Okay, we're jumping in the air, now what?
        if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD, Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]:
            if self.height_level == 3:
                # Up-air right away
                # Drift towards the spot
                controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                controller.tilt_analog(Button.BUTTON_C, 0.5, 1)
                return
            jump_on_frame = 2
            if self.height_level == 5:
                jump_on_frame = 6
            if self.height_level == 6:
                jump_on_frame = 12
            # Double jump on jumping frame 2
            if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
                if smashbot_state.action_frame == jump_on_frame:
                    controller.press_button(Button.BUTTON_Y)
                    controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                    return
                else:
                    controller.release_button(Button.BUTTON_Y)
                    controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                    return
            # Attack on DJ frame 2
            if smashbot_state.action in [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]:
                if smashbot_state.action_frame == 2:
                    controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                    controller.tilt_analog(Button.BUTTON_C, 0.5, 1)
                    return
                else:
                    controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                    controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
                    return

            # Up-air right away
            # Drift towards the spot
            controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
            controller.tilt_analog(Button.BUTTON_C, 0.4, 1)
            return

        # Drift in during the attack
        if smashbot_state.action in [Action.UAIR, Action.BAIR, Action.DAIR, Action.FAIR, Action.NAIR]:
            controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
            return

        self.interruptible = True
        controller.release_all()
