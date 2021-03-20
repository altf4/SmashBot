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

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        #   1) Short hop height -> 10.65
        #   2) Full hop, falling up air -> 20 (22 frames)
        #   3) Full hop height -> 30 (19 frames)
        #   4) Jump, immediate double jump -> 40 (19 frames) (dj on jump frame 2) (attack on dj frame 2)
        #   5) Jump, wait, double jump -> 50
        #   6) Jump wait a bit more, jump -> 60
        #   7) Full jump, double jump -> 70

        #DJ -> 40 units

        # If we're in knee bend, let go of jump. But move toward opponent
        if smashbot_state.action == Action.KNEE_BEND:
            self.interruptible = False
            controller.release_button(Button.BUTTON_Y)
            jumpdirection = 1
            if opponent_state.position.x < smashbot_state.position.x:
                jumpdirection = 0
            controller.tilt_analog(Button.BUTTON_MAIN, jumpdirection, .5)
            return

        # If we're on the ground, but NOT in knee bend, then jump
        if smashbot_state.on_ground:
            if controller.prev.button[Button.BUTTON_Y]:
                self.interruptible = True
                controller.empty_input()
            else:
                self.interruptible = False
                controller.press_button(Button.BUTTON_Y)
            return

        # If we're falling, then press down hard to do a fast fall, and press L to L cancel
        if smashbot_state.speed_y_self < 0:
            self.interruptible = False
            # Don't jump right off the stage like an idiot
            #   If we're close to the edge, angle back in
            x = 0.5
            edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
            if opponent_state.position.x < 0:
                edge_x = -edge_x
            edgedistance = abs(edge_x - smashbot_state.position.x)
            if edgedistance < 15:
                x = int(smashbot_state.position.x < 0)

            controller.tilt_analog(Button.BUTTON_MAIN, x, 0)
            # Only do the L cancel near the end of the animation
            if smashbot_state.action_frame >= 12:
                controller.press_button(Button.BUTTON_L)
            return

        # Once we're airborn, do an attack
        if not self.framedata.is_attack(smashbot_state.character, smashbot_state.action):
            # If the C stick wasn't set to middle, then
            if controller.prev.c_stick != (.5, .5):
                controller.tilt_analog(Button.BUTTON_C, .5, .5)
                return

            if self.direction == SHFFL_DIRECTION.UP:
                controller.tilt_analog(Button.BUTTON_C, .5, 1)
            if self.direction == SHFFL_DIRECTION.DOWN:
                controller.tilt_analog(Button.BUTTON_C, .5, 0)
            if self.direction == SHFFL_DIRECTION.FORWARD:
                controller.tilt_analog(Button.BUTTON_C, int(smashbot_state.facing), .5)
            if self.direction == SHFFL_DIRECTION.BACK:
                controller.tilt_analog(Button.BUTTON_C, int(not smashbot_state.facing), .5)
            if self.direction == SHFFL_DIRECTION.NEUTRAL:
                controller.press_button(Button.BUTTON_A)
                controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)
            return
        elif smashbot_state.speed_y_self > 0:
            # Don't jump right off the stage like an idiot
            #   If we're close to the edge, angle back in
            x = 0.5
            edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
            if opponent_state.position.x < 0:
                edge_x = -edge_x
            edgedistance = abs(edge_x - smashbot_state.position.x)
            if edgedistance < 15:
                x = int(smashbot_state.position.x < 0)

            controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
            controller.tilt_analog(Button.BUTTON_C, .5, .5)
            controller.release_button(Button.BUTTON_L)
            return

        self.interruptible = True
        controller.empty_input()
