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
    def __init__(self, target_x, target_y, direction=AIR_ATTACK_DIRECTION.DOWN):
        self.direction = direction
        self.target_x = target_x
        self.target_y = target_y

    def frame_commitment(target_y):
        """Given the target height, how many frames worth of commitment does it require?"""
        if 5 < target_y <= 15:
            return 500 # Height 1 maybe remove
        if 15 < target_y <= 30:
            return 500 # Height 2 (heigher because we need to drop-down upair) 22
        if 30 < target_y <= 40:
            return 15 # Height 3
        if 40 < target_y <= 50:
            return 19 # Height 4
        if 50 < target_y <= 60:
            return 23 # Height 5
        if 60 < target_y <= 70:
            return 29 # Height 6
        if 70 < target_y <= 80:
            return 28 # Height 7 # TODO
        return 500

    def height_levels():
        """Returns a list of the possible attack height levels"""
        return [1, 2, 3, 4, 5, 6, 7]

    def attack_height(height_level):
        """For a given height level, returns the height of our attack"""
        if height_level == 1:
            return 0
        if height_level == 2:
            return 0
        if height_level == 3:
            return 31
        if height_level == 4:
            return 43
        if height_level == 5:
            return 55
        if height_level == 6:
            return 66
        if height_level == 7:
            return 0
        return 0

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        #   1) Short hop height -> 10.65 (maybe don't use)
        #   2) Full hop, falling up air -> 20 (22 frames)
        #   3) Full hop height -> 30 (19 frames)
        #   4) Jump, immediate double jump -> 40 (19 frames) (dj on jump frame 2) (attack on dj frame 2)
        #   5) Jump, wait, double jump -> 50
        #   6) Jump wait a bit more, jump -> 60
        #   7) Full jump, double jump -> 70

        # TODO adjust for starting height. Like on a platform

        height_level = 0
        if 15 < self.target_y <= 30:
            height_level = 2
        if 30 < self.target_y <= 40:
            height_level = 3
        if 40 < self.target_y <= 50:
            height_level = 4
        if 50 < self.target_y <= 60:
            height_level = 5
        if 60 < self.target_y <= 70:
            height_level = 6
        if 70 < self.target_y <= 80:
            height_level = 7
        #DJ -> 40 units

        # Landing. We're done
        if smashbot_state.action in [Action.LANDING, Action.UAIR_LANDING]:
            self.interruptible = True
            controller.release_all()
            return

        # TODO dash over to the location first?

        # Full hop
        if smashbot_state.on_ground:
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
            if controller.prev.button[Button.BUTTON_Y] and smashbot_state.action != Action.KNEE_BEND:
                controller.release_button(Button.BUTTON_Y)
                return
            else:
                controller.press_button(Button.BUTTON_Y)
                controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                return

        # falling back down
        if smashbot_state.speed_y_self < 0:
            # TODO L-cancel? maybe only on height 1?

            # Drift onto stage if we're near the edge
            if abs(smashbot_state.position.x) + 10 > melee.stages.EDGE_GROUND_POSITION[gamestate.stage]:
                controller.tilt_analog(Button.BUTTON_MAIN, int(smashbot_state.position.x < 0), .5)
                return
            else:
                # fastfall
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0)
                return

        # Okay, we're jumping in the air, now what?
        if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD, Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]:
            if height_level == 3:
                # Up-air right away
                # Drift towards the spot
                controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                controller.tilt_analog(Button.BUTTON_C, 0.5, 1)
                return
            jump_on_frame = 2
            if height_level == 5:
                jump_on_frame = 6
            if height_level == 6:
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
