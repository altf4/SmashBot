import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# ArmadaShine
class ArmadaShine(Chain):
    def inrange():
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        # Can we armada shine?
        #   To do this, let's assume that we have to hit the opponent in the cooldown of an attack
        #   or in a laggy non-attack animation.
        # This means we have to hit them in the window of time between the last hitbox frame (if present)
        #   and the last unactionable frame of the action
        start, end = ArmadaShine.framewindow()
        frames_x, frames_y = ArmadaShine.traveltime()

        globals.logger.log("Notes", "window: " + str([start, end]) + " ", concat=True)
        globals.logger.log("Notes", "frames: " + str([frames_x, frames_y]) + " ", concat=True)

        # Can we do the armada shine?
        if frames_x < end and frames_y < end:
            return True
        return False

    def framewindow():
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        start, end = -1, -1
        # Is opponent attacking?
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            start = globals.framedata.lasthitboxframe(opponent_state.character, opponent_state.action)
            end = globals.framedata.iasa(opponent_state.character, opponent_state.action)
        # Else, is opponent in a "b" move?
        elif globals.framedata.isbmove(opponent_state.character, opponent_state.action):
            start = 1
            end = globals.framedata.lastframe(opponent_state.character, opponent_state.action)
        return start, end

    def traveltime():
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # Calculate the target_x and target_y
        #TODO For now let's assume they stay still. But we need to count locomotion
        target_x, target_y = opponent_state.x, opponent_state.y

        shorthopheight = 10.62
        jumpheight = 31.28
        doublejumpheight = 40.20

        shorthopapexframes = 10
        jumpapexframes = 16
        doublejumpapexframes = 19

        slowfallspeed = 2.8
        fastfallspeed = 3.4

        # How long will it take us to get to opponent? vertically and horizontally
        frames_y = -1
        # It takes about 9 frames to run off the stage from where we start
        frames_x = 9

        opponentedgedistance = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(opponent_state.x))
        edgedistance = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        speed = 1.7
        friction = .02

        # How many horizontal frames will it take?
        while opponentedgedistance > 0:
            opponentedgedistance -= speed
            speed -= friction
            speed = max(speed, 0.819625854)
            frames_x += 1

        #TODO Y

        return frames_x, frames_y

    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # How are we going to do the shine? There's 6 options:
        #   1) Full jump then double jump
        #   2) Full jump directly to opponent
        #   3) Short hop then double jump
        #   4) Short hop directly to opponent
        #   5) Run off then double jump
        #   6) Run off directly to opponent
        start, end = ArmadaShine.framewindow()
        frames_x, frames_y = ArmadaShine.traveltime()

        globals.logger.log("Notes", "frames: " + str([frames_x, frames_y, smashbot_state.speed_air_x_self]) + " ", concat=True)


        # If we're in range... do the shine!
        if globals.gamestate.distance < 11.8:
            self.interruptible = True
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            controller.press_button(Button.BUTTON_B)
            return

        x = 0
        if smashbot_state.x < opponent_state.x:
            x = 1

        edgedistance = abs(melee.stages.edgeposition(globals.gamestate.stage) - abs(smashbot_state.x))

        # If we're on the stage still...
        if smashbot_state.on_ground:
            # But not close, run at it
            if edgedistance > 11:
                self.interruptible = True
                # Keep pressing what we were pressing if we're turning
                if smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
                    return
                controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
                return
            # Jump off the stage
            else:
                self.interruptible = False
                controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
                controller.press_button(Button.BUTTON_Y)
                return

        # If we're off the stage, we need to keep pushing in towards our opponent
        if smashbot_state.off_stage:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
            controller.release_button(Button.BUTTON_B)
            controller.release_button(Button.BUTTON_Y)
            return

        self.interruptible = True
        controller.empty_input()
