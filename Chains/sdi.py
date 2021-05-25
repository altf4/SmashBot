import math

import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain

class SDI(Chain):
    def __init__(self):
        self.cardinal = None

    def angle_to_cardinal(angle):
        """For the given angle, return the nearest cardinal (8 directions) direction"""
        if angle <= 22.5 or 337.5 < angle:
            return 1, 0.5
        if 22.5 < angle <= 67.5:
            return 1, 1
        if 67.5 < angle <= 112.5:
            return 0.5, 1
        if 112.5 < angle <= 157.5:
            return 0, 1
        if 157.5 < angle <= 202.5:
            return 0, 0.5
        if 202.5 < angle <= 247.5:
            return 0, 0
        if 247.5 < angle <= 292.5:
            return 0.5, 0
        if 292.5 < angle <= 337.5:
            return 1, 0

        # This shouldn't be possible, but just in case
        return 1, 1

    def cardinal_left(cardinal):
        """For the given cardinal, return the cardinal to the left of it"""
        if cardinal == (1, 0.5):
            return 1, 1
        if cardinal == (1, 1):
            return 0.5, 1
        if cardinal == (0.5, 1):
            return 0, 1
        if cardinal == (0, 1):
            return 0, 0.5
        if cardinal == (0, 0.5):
            return 0, 0
        if cardinal == (0, 0):
            return 0.5, 0
        if cardinal == (0.5, 0):
            return 1, 0
        if cardinal == (1, 0):
            return 1, 0.5

        # This shouldn't be possible, but just in case
        return 1, 1

    def cardinal_right(cardinal):
        """For the given cardinal, return the cardinal to the left of it"""
        if cardinal == (1, 0.5):
            return 1, 0
        if cardinal == (1, 0):
            return 0.5, 0
        if cardinal == (0.5, 0):
            return 0, 0
        if cardinal == (0, 0):
            return 0, 0.5
        if cardinal == (0, 0.5):
            return 0, 1
        if cardinal == (0, 1):
            return 0.5, 1
        if cardinal == (0.5, 1):
            return 1, 1
        if cardinal == (1, 1):
            return 1, 0.5

        # This shouldn't be possible, but just in case
        return 1, 1

    def touching_ground(smashbot_state):
        """Returns whether we're on top of the ground, but not necessarily triggering the on_ground flag

        If we're on the ground, we don't want to DI down, so it's important to know
        """
        # Todo: consider platforms
        if smashbot_state.on_ground:
            return True

        if abs(smashbot_state.position.y) < 0.25:
            return True

    """Smash DI"""
    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        # There's three kinds of SDI:
        #   1) Survival SDI
        #   2) Combo SDI
        #   3) Situationally-specific SDI

        # SDI implementation
        # We break up SDI into 8 possible directions. 4 cardinal directions and 4 diagonals
        #   Every SDI targets one of these 8 directions and wiggles back and forth accross the direction

        # If we've committed to a given SDI direction, stick with it no matter what
        if self.cardinal is not None:
            if self.logger:
                self.logger.log("Notes", " Committed SDI cardinal: " + str(self.cardinal) + " ", concat=True)
            if SDI.touching_ground(smashbot_state):
                # If we're on the ground, and want to move horizontally, just alternate neutral and the direction
                #   This will avoid accidentally moving upwards
                if self.cardinal[1] == 0.5:
                    if gamestate.frame % 2:
                        controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
                    else:
                        controller.tilt_analog(Button.BUTTON_MAIN, self.cardinal[0], 0.5)
                    return
            if gamestate.frame % 2:
                x, y = SDI.cardinal_right(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = SDI.cardinal_left(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return

        # Situationally-specifci SDI
        #   Some hits require specific SDI to get out of a tricky combo. Account for those first, here

        # These moves are a kind of tornado. If you fight against it, you actually just wind up back in. In order to get out,
        #   we need to SDI in the direction that we're being hit / up
        if opponent_state.character in [Character.PEACH, Character.PIKACHU, Character.SAMUS, Character.SHEIK] and opponent_state.action == Action.DOWNSMASH:
            angle = math.degrees(-math.atan2(smashbot_state.speed_x_attack, smashbot_state.speed_y_attack)) + 90
            self.cardinal = SDI.angle_to_cardinal(angle)
            self.cardinal = (self.cardinal[0], 1)
            if self.logger:
                self.logger.log("Notes", " Downsmash SDI angle: " + str(angle) + " ", concat=True)
            if gamestate.frame % 2:
                x, y = SDI.cardinal_right(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = SDI.cardinal_left(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return

        # TODO: SDI Into the ground to tech?

        # We're off the stage, so let's SDI back onto the stage
        if smashbot_state.off_stage:
            cardinal = (int(smashbot_state.position.x < 0), int(smashbot_state.position.y < 0))
            if self.logger:
                self.logger.log("Notes", " Off-stage SDI cardinal: " + str(cardinal) + " ", concat=True)

            if gamestate.frame % 2:
                x, y = SDI.cardinal_right(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = SDI.cardinal_left(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return


        absolute_speed = math.sqrt(smashbot_state.speed_x_attack ** 2 + smashbot_state.speed_y_attack ** 2)

        # Survival SDI
        #   If we're at risk of dying from the hit, then SDI backwards to go further back to cut into the knockback
        if smashbot_state.percent > 60 and absolute_speed > 3:
            # Amsah tech
            #   If we're in survival DI, and near the ground, then let's Amsah tech
            if smashbot_state.position.y < 6:
                self.cardinal = (int(smashbot_state.position.x < 0), 0)
            else:
                angle = math.degrees(-math.atan2(smashbot_state.speed_x_attack, smashbot_state.speed_y_attack)) + 90
                # Which cardinal direction is the most opposite the direction?
                angle = (angle + 180) % 360
                self.cardinal = SDI.angle_to_cardinal(angle)
                if self.logger:
                    self.logger.log("Notes", " Survival SDI angle: " + str(angle) + " " + str(smashbot_state.speed_y_attack) + " " + str(smashbot_state.speed_x_attack), concat=True)

                # If on ground, then we can't SDI up or down
                if smashbot_state.on_ground:
                    if angle < 90 or angle > 270:
                        self.cardinal = (1, 0.5)
                    else:
                        self.cardinal = (0, 0.5)

                # If we're not ON the actual ground, but touching it, then don't SDI down
                if SDI.touching_ground(smashbot_state):
                    if self.cardinal[1] == 0:
                        self.cardinal = (self.cardinal[0], 0.5)
                        if self.cardinal[0] == 0.5:
                            self.cardinal = (1, 0.5)

            if gamestate.frame % 2:
                x, y = SDI.cardinal_right(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = SDI.cardinal_left(self.cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return

        # Combo SDI
        #   SDI away from the opponent to keep from from following up
        angle = math.degrees(-math.atan2(smashbot_state.position.x - opponent_state.position.x, smashbot_state.position.y - opponent_state.position.y)) + 90
        angle = (angle + 360) % 360
        self.cardinal = SDI.angle_to_cardinal(angle)
        if self.logger:
            self.logger.log("Notes", " Combo SDI angle: " + str(angle) + " ", concat=True)

        # If on ground, then we can't SDI up or down
        if smashbot_state.on_ground:
            if angle < 90 or angle > 270:
                self.cardinal = (1, 0.5)
            else:
                self.cardinal = (0, 0.5)

        # If we're not ON the actual ground, but touching it, then don't SDI down
        if SDI.touching_ground(smashbot_state):
            if self.cardinal[1] == 0:
                self.cardinal = (self.cardinal[0], 0.5)
                if self.cardinal[0] == 0.5:
                    self.cardinal = (1, 0.5)
            # If we're on the ground, and want to move horizontally, just alternate neutral and the direction
            #   This will avoid accidentally moving upwards
            if self.cardinal[1] == 0.5:
                if gamestate.frame % 2:
                    controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 0.5)
                else:
                    controller.tilt_analog(Button.BUTTON_MAIN, self.cardinal[0], 0.5)
                return

        if gamestate.frame % 2:
            x, y = SDI.cardinal_right(self.cardinal)
            controller.tilt_analog(Button.BUTTON_MAIN, x, y)
        else:
            x, y = SDI.cardinal_left(self.cardinal)
            controller.tilt_analog(Button.BUTTON_MAIN, x, y)
        return
