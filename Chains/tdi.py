import math
import random

import melee
from melee.enums import Action, Button, Character
from Chains.chain import Chain
from Chains.sdi import SDI

class TDI(Chain):
    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller
        self.interruptible = True

        # There's three kinds of TDI:
        #   1) Survival TDI
        #   2) Combo TDI
        #   3) Situationally-specific TDI

        # ASDI down
        if not (opponent_state.character in [Character.PEACH, Character.PIKACHU, Character.SAMUS, Character.SHEIK] and opponent_state.action == Action.DOWNSMASH):
            controller.tilt_analog(Button.BUTTON_C, 0.5, 0)

        absolute_speed = math.sqrt(smashbot_state.speed_x_attack ** 2 + smashbot_state.speed_y_attack ** 2)

        # Survival TDI
        #   If we're at risk of dying from the hit, then TDI 90 degrees from the direction of the hit
        if smashbot_state.percent > 60 and absolute_speed > 3:
            # Amsah tech
            #   If we're in survival DI, and near the ground, then let's Amsah tech
            angle = (math.degrees(-math.atan2(smashbot_state.speed_x_attack, smashbot_state.speed_y_attack)) + 90) % 360

            if smashbot_state.position.y < 6:
                if 0 <= angle <= 40:
                    angle = (angle - 90) % 360
                elif 40 < angle <= 90:
                    angle = (angle + 90) % 360
                elif 90 < angle <= 140:
                    angle = (angle - 90) % 360
                elif 140 < angle <= 180:
                    angle = (angle + 90) % 360
                else:
                    # TODO What situation would this be? We're being hit downward, so I guess just DI into the stage
                    angle = 0
                    if smashbot_state.position.x > 0:
                        angle = 180
                cardinal = SDI.angle_to_cardinal(angle)
                if gamestate.custom["tech_lockout"] == 0:
                    controller.press_button(Button.BUTTON_L)
                else:
                    controller.release_button(Button.BUTTON_L)

            else:
                # TODO which 90 degree angle? Randomize for now
                if random.randint(0, 1) == 0:
                    angle = (angle + 90) % 360
                else:
                    angle = (angle - 90) % 360
                cardinal = SDI.angle_to_cardinal(angle)
            controller.tilt_analog(Button.BUTTON_MAIN, cardinal[0], cardinal[1])
            return

        # Combo TDI
        #   TDI away from the opponent to keep from from following up
        angle = math.degrees(-math.atan2(smashbot_state.position.x - opponent_state.position.x, smashbot_state.position.y - opponent_state.position.y)) + 90
        angle = (angle + 360) % 360
        cardinal = SDI.angle_to_cardinal(angle)
        if self.logger:
            self.logger.log("Notes", " Combo TDI angle: " + str(angle) + " ", concat=True)

        # If on ground, then we can't TDI up or down
        if smashbot_state.on_ground:
            if angle < 90 or angle > 270:
                cardinal = (1, 0.5)
            else:
                cardinal = (0, 0.5)

        # If we're not ON the actual ground, but touching it, then don't TDI down
        if SDI.touching_ground(smashbot_state):
            if cardinal[1] == 0:
                cardinal = (cardinal[0], 0.5)
                if cardinal[0] == 0.5:
                    cardinal = (1, 0.5)
            # Don't tech if we're close to the edge. We're better off doing a slideoff
            if abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.position.x)) > 30:
                if gamestate.custom["tech_lockout"] == 0:
                    controller.press_button(Button.BUTTON_L)
                else:
                    controller.release_button(Button.BUTTON_L)

        controller.tilt_analog(Button.BUTTON_MAIN, cardinal[0], cardinal[1])
