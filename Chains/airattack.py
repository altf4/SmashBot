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
        if 15 < target_y <= 30:
            return 500 # Height 2 (heigher because we need to drop-down upair) 22
        if 30 < target_y <= 40:
            return 15 # Height 3
        if 40 < target_y <= 50:
            return 19 # Height 4
        if 50 < target_y <= 60:
            return 23 # Height 5
        if 55 < target_y <= 65:
            return 25 # Height 6 # TODO
        if 65 < target_y <= 75:
            return 28 # Height 7 # TODO
        return 500

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
        if 15 < self.target_y <= 25:
            height_level = 2
        if 25 < self.target_y <= 35:
            height_level = 3
        if 35 < self.target_y <= 45:
            height_level = 4
        if 45 < self.target_y <= 55:
            height_level = 5
        if 55 < self.target_y <= 65:
            height_level = 6
        if 65 < self.target_y <= 75:
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
            if height_level == 4:
                # Double jump on jumping frame 2
                if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
                    if smashbot_state.action_frame == 2:
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
            if height_level == 5:
                # Double jump on jumping frame 6
                if smashbot_state.action in [Action.JUMPING_FORWARD, Action.JUMPING_BACKWARD]:
                    if smashbot_state.action_frame == 6:
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


                controller.release_all()
                return
            else:
                # Up-air right away
                # Drift towards the spot
                controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
                controller.tilt_analog(Button.BUTTON_C, 0.5, 1)
                return

        # Drift in during the attack
        if smashbot_state.action in [Action.UAIR, Action.BAIR, Action.DAIR, Action.FAIR, Action.NAIR]:
            controller.tilt_analog(Button.BUTTON_MAIN, int(self.target_x > smashbot_state.position.x), .5)
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0.5)
            return

        self.interruptible = True
        controller.release_all()
