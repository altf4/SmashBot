import math

import melee
from melee.enums import Action, Button
from Chains.chain import Chain

class SDI(Chain):

    def _angle_to_cardinal(self, angle):
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

    def _cardinal_left(self, cardinal):
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

    def _cardinal_right(self, cardinal):
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

        # Situationally-specifci SDI
        #   Some hits require specific SDI to get out of a tricky combo. Account for those first, here

        # TODO: SDI Into the ground to tech?

        # We're off the stage, so let's SDI back onto the stage
        if smashbot_state.off_stage:
            cardinal = (int(smashbot_state.position.x < 0), int(smashbot_state.position.y < 0))
            self.logger.log("Notes", " Off-stage SDI cardinal: " + str(cardinal) + " ", concat=True)

            if gamestate.frame % 2:
                x, y = self._cardinal_right(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = self._cardinal_left(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return


        absolute_speed = math.sqrt(smashbot_state.speed_x_attack ** 2 + smashbot_state.speed_y_attack ** 2)
        if self.logger:
            self.logger.log("Notes", " absolute_speed: " + str(absolute_speed) + " ", concat=True)

        # Survival SDI
        #   If we're at risk of dying from the hit, then SDI backwards to go further back to cut into the knockback
        if smashbot_state.percent > 60 and absolute_speed > 3:
            angle = math.degrees(math.atan2(smashbot_state.speed_y_attack, smashbot_state.speed_x_attack))
            # Which cardinal direction is the most opposite the direction?
            angle = (angle + 180) % 360
            cardinal = self._angle_to_cardinal(angle)

            self.logger.log("Notes", " Survival SDI angle: " + str(angle) + " ", concat=True)

            # If on ground, then we can't SDI up or down
            if smashbot_state.on_ground:
                if angle < 90 or angle > 270:
                    cardinal = (1, 0.5)
                else:
                    cardinal = (0, 0.5)

            if gamestate.frame % 2:
                x, y = self._cardinal_right(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            else:
                x, y = self._cardinal_left(cardinal)
                controller.tilt_analog(Button.BUTTON_MAIN, x, y)
            return

        # Combo SDI
        #   SDI away from the opponent to keep from from following up
        angle = math.degrees(math.atan2(smashbot_state.position.x - opponent_state.position.x, smashbot_state.position.y - opponent_state.position.y))
        angle = (angle + 360) % 360
        # angle = (angle + 180) % 360
        cardinal = self._angle_to_cardinal(angle)
        self.logger.log("Notes", " Combo DI angle: " + str(angle) + " ", concat=True)

        # If on ground, then we can't SDI up or down
        if smashbot_state.on_ground:
            if angle < 90 or angle > 270:
                cardinal = (1, 0.5)
            else:
                cardinal = (0, 0.5)

        if gamestate.frame % 2:
            x, y = self._cardinal_right(cardinal)
            controller.tilt_analog(Button.BUTTON_MAIN, x, y)
        else:
            x, y = self._cardinal_left(cardinal)
            controller.tilt_analog(Button.BUTTON_MAIN, x, y)
        return
