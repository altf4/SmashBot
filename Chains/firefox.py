import melee
import random
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class FIREFOX(Enum):
    HIGH = 0
    MEDIUM = 1
    EDGE = 2
    RANDOM = 3

class Firefox(Chain):
    def __init__(self, direction=FIREFOX.RANDOM):
        if direction == FIREFOX.RANDOM:
            self.direction = FIREFOX(random.randint(0, 2))
        else:
            self.direction = direction

    def getangle(self, gamestate, smashbot_state):
        x = 0
        if smashbot_state.x < 0:
            x = 1

        # The point we grab the edge at is a little below the stage
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.x))
        diff_y = abs(smashbot_state.y + 5)
        larger_magnitude = max(diff_x, diff_y)

        # Scale down values to between 0 and 1
        x = diff_x / larger_magnitude
        y = diff_y / larger_magnitude

        # Now scale down to be between .5 and 1
        if smashbot_state.x < 0:
            x = (x/2) + 0.5
        else:
            x = 0.5 - (x/2)
        if smashbot_state.y < 0:
            y = (y/2) + 0.5
        else:
            y = 0.5 - (y/2)
        return x, y

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        # We're done here if...
        if smashbot_state.on_ground or smashbot_state.action in [Action.EDGE_CATCHING, Action.EDGE_HANGING]:
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

        x = 0
        if smashbot_state.x < 0:
            x = 1

        # Which way should we point?
        if smashbot_state.action == Action.FIREFOX_WAIT_AIR:
            self.interruptible = False
            diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.x))

            if self.direction == FIREFOX.HIGH and diff_x < 50:
                controller.tilt_analog(Button.BUTTON_MAIN, x, 1)
            if self.direction == FIREFOX.MEDIUM and smashbot_state.y > -10:
                controller.tilt_analog(Button.BUTTON_MAIN, x, .5)
            if self.direction == FIREFOX.EDGE:
                x, y = self.getangle(gamestate, smashbot_state)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return

        # Is this a "forbidden" angle? Don't try it if it is.
        if self.direction == FIREFOX.EDGE:
            x, y = self.getangle(gamestate, smashbot_state)
            # Let's add a little extra room so we don't miscalculate
            # if .3625 < y < .6375 or .3625 < x < .6375:
            if (.3525 < y < .6475) or (.3525 < x < .6475) and (smashbot_state.y > -15):
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
