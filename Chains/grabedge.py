import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# Grab the edge
class Grabedge(Chain):
    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # Where is the edge that we're going to?
        edge_x = melee.stages.edgegroundposition(globals.gamestate.stage)
        if smashbot_state.x < 0:
            edge_x = -edge_x

        # If we're on the edge, then we're done here, end the chain
        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're in spotdodge, do nothing
        if smashbot_state.action == Action.SPOTDODGE:
            self.interruptible = True
            controller.empty_input()
            return

        # If we're stuck wavedashing, just hang out and do nothing
        if smashbot_state.action == Action.LANDING_SPECIAL and smashbot_state.action_frame < 28:
            self.interruptible = True
            controller.empty_input()
            return

        #If we're walking, stop for a frame
        #Also, if we're shielding, don't try to dash. We will accidentally roll
        if smashbot_state.action == Action.WALK_SLOW or \
            smashbot_state.action == Action.WALK_MIDDLE or \
            smashbot_state.action == Action.WALK_FAST or \
            smashbot_state.action == Action.SHIELD_START or \
            smashbot_state.action == Action.SHIELD_REFLECT or \
            smashbot_state.action == Action.SHIELD:
                self.interruptible = True
                controller.empty_input()
                return

        facinginwards = smashbot_state.facing == (smashbot_state.x < 0)
        if not facinginwards and smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
            facinginwards = True

        edgedistance = abs(edge_x - smashbot_state.x)
        turnspeed = abs(smashbot_state.speed_ground_x_self)
        # If we turn right now, what will our speed be?
        if smashbot_state.action == Action.DASHING:
            turnspeed = (abs(smashbot_state.speed_ground_x_self) - 0.32) / 4
        slidedistance = globals.framedata.slidedistance(smashbot_state, turnspeed, 7)
        closetoedge = edgedistance < slidedistance

        # This is actually shine turnaround
        if smashbot_state.action == Action.MARTH_COUNTER:
            self.interruptible = False
            controller.empty_input()
            return

        # Fastfall, but only once
        if smashbot_state.action == Action.FALLING:
            self.interruptible = False

            # Should we shine?
            canhit = globals.gamestate.distance < 11.8 and opponent_state.invulnerability_left == 0
            if (smashbot_state.y < -15) or canhit:
                controller.press_button(Button.BUTTON_B)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
                return

            # Fastfall speed is 3.4, but we need a little wiggle room
            if smashbot_state.speed_y_self > -3.35:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 0)
            else:
                # DI in to the opponent
                x = 0
                if smashbot_state.x < opponent_state.x:
                    x = 1
                controller.tilt_analog(melee.Button.BUTTON_MAIN, x, 0.5)
            return

        # Shine turnaround
        if smashbot_state.action == Action.DOWN_B_STUN and not facinginwards:
            self.interruptible = False
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
            return

        # Jump out of shine
        if smashbot_state.action == Action.DOWN_B_AIR and facinginwards:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Firefox to grab edge
        if smashbot_state.action == Action.JUMPING_ARIAL_FORWARD:
            self.interruptible = False
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0.5, 1)
            return

        self.interruptible = True

        # Pivot slide
        if smashbot_state.action == Action.TURNING and facinginwards and closetoedge:
            controller.empty_input()
            return

        # Do the turn
        if smashbot_state.action == Action.DASHING and closetoedge:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
            return

        #If we're starting the turn around animation, keep pressing that way or
        #   else we'll get stuck in the slow turnaround
        if smashbot_state.action == Action.TURNING and smashbot_state.action_frame == 1:
            return

        #Dash back, since we're about to start running
        # #Action.FOX_DASH_FRAMES
        if smashbot_state.action == Action.DASHING and smashbot_state.action_frame >= 11:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
            return

        #We can't dash IMMEDIATELY after landing. So just chill for a bit
        if smashbot_state.action == Action.LANDING and smashbot_state.action_frame < 2:
            controller.empty_input()
            return

        #Are we outside the given radius of dash dancing?
        if smashbot_state.x < edge_x:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return

        if smashbot_state.x > edge_x:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            return

        #Keep running the direction we're going
        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
        return
