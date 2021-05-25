import melee
import math
import random
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class FIREFOX(Enum):
    HIGH = 0
    EDGE = 1
    HORIZONTAL = 2
    RANDOM = 3
    # Added SAFERANDOM option so Smashbot wouldn't random a straight horizontal upB and SD below the stage
    SAFERANDOM = 4

class Firefox(Chain):
    def __init__(self, direction=FIREFOX.RANDOM):
        if direction == FIREFOX.RANDOM:
            self.direction = FIREFOX(random.randint(0, 2))
        elif direction == FIREFOX.SAFERANDOM:
            self.direction = FIREFOX(random.randint(0, 1))
        else:
            self.direction = direction

    def get_low_corner(self, stage):
        """Returns the (x, y) coords of the lowest point of the stage where we can ride up the wall

        Basically, we need to aim ABOVE this point, or we'll FF below the stage.
        """
        if stage == melee.Stage.YOSHIS_STORY:
            return (melee.EDGE_POSITION[stage], -1000)
        if stage == melee.Stage.BATTLEFIELD:
            return (melee.EDGE_POSITION[stage], -10)
        if stage == melee.Stage.FINAL_DESTINATION:
            return (45, -66.21936)
        if stage == melee.Stage.DREAMLAND:
            return (63, -47.480972)
        if stage == melee.Stage.POKEMON_STADIUM:
            return (70, -29.224771)

        return (0, 0)

    def getangle(self, gamestate, smashbot_state):
        # Make sure we don't angle below the stage's low corner.
        #   If we do, we'll SD
        corner_x, corner_y = self.get_low_corner(gamestate.stage)

        # The point we grab the edge at is a little below the stage
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.position.x))
        diff_y = abs(smashbot_state.position.y + 5)
        larger_magnitude = max(diff_x, diff_y)

        # Scale down values to between 0 and 1
        x = diff_x / larger_magnitude
        y = diff_y / larger_magnitude

        # Now scale down to be between .5 and 1
        if smashbot_state.position.x < 0:
            x = (x/2) + 0.5
            corner_x *= -1
        else:
            x = 0.5 - (x/2)
        if smashbot_state.position.y < 0:
            y = (y/2) + 0.5
        else:
            y = 0.5 - (y/2)

        # Only bother with corner adjustment when FF upwards
        if smashbot_state.position.y < -10:
            wanted_angle = math.degrees(-math.atan2(x - 0.5, y - 0.5)) % 360
            lowest_angle = math.degrees(-math.atan2(corner_x - smashbot_state.position.x, corner_y - smashbot_state.position.y)) % 360

            if smashbot_state.position.x > 0:
                # On the right, lower angle is higher
                if lowest_angle < wanted_angle:
                    return 0.5, 1 #TODO make a better angle here.
            else:
                # On the left, lower angle is lower
                if wanted_angle < lowest_angle:
                    return 0.5, 1 #TODO make a better angle here.

        return x, y

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        # We're done here if...
        if smashbot_state.on_ground or smashbot_state.action in [Action.EDGE_CATCHING, Action.EDGE_HANGING, Action.SWORD_DANCE_1_AIR]:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're traveling in the air, let go of the stick
        if smashbot_state.action in [Action.FIREFOX_AIR, Action.DEAD_FALL]:
            self.interruptible = False
            controller.empty_input()
            return

        # We need to jump out of our shine
        if smashbot_state.action in [Action.DOWN_B_AIR, Action.DOWN_B_STUN]:
            controller.release_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
            if controller.prev.button[Button.BUTTON_Y]:
                controller.release_button(Button.BUTTON_Y)
            else:
                controller.press_button(Button.BUTTON_Y)
            return

        x = int(smashbot_state.position.x < 0)
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.position.x))
        # Which way should we point?
        if smashbot_state.action == Action.FIREFOX_WAIT_AIR:
            self.interruptible = False
            if self.direction == FIREFOX.HIGH:
                if diff_x > 20:
                    controller.tilt_analog(Button.BUTTON_MAIN, x, 1)
                    return
                else:
                    controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
                    return
            if self.direction == FIREFOX.HORIZONTAL and smashbot_state.position.y > -10:
                controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
                return
            if self.direction == FIREFOX.EDGE:
                x, y = self.getangle(gamestate, smashbot_state)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
                return
            controller.tilt_analog(Button.BUTTON_MAIN, x, 1)
            return

        # Is this a "forbidden" angle? Don't try it if it is.
        if self.direction == FIREFOX.EDGE:
            x, y = self.getangle(gamestate, smashbot_state)
            # Let's add a little extra room so we don't miscalculate
            # if .3625 < y < .6375 or .3625 < x < .6375:
            if (.3525 < y < .6475) or (.3525 < x < .6475) and (smashbot_state.position.y > -15):
                # Unless we're in range to just grab the edge. Then the angle doesn't matter
                if not ((-16.4 < smashbot_state.position.y < -5) and (diff_x < 10)):
                    controller.empty_input()
                    return

        # If we already pressed B last frame, let go
        if controller.prev.button[Button.BUTTON_B]:
            self.interruptible = True
            controller.empty_input()
            return
        controller.press_button(Button.BUTTON_B)
        controller.tilt_analog(Button.BUTTON_MAIN, .5, 1)
        self.interruptible = False
