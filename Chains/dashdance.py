import melee
import globals
from Chains.chain import Chain

class DashDance(Chain):
    def __init__(self, pivot, radius=0):
        self.pivotpoint = pivot
        self.radius = radius

    def step(self):
        gamestate = globals.gamestate
        controller = globals.controller
        smashbot_state = globals.smashbot_state

        #TODO: Moonwalk protection

        # If we're stuck wavedashing, just hang out and do nothing
        if smashbot_state.action == melee.Action.LANDING_SPECIAL and smashbot_state.action_frame < 28:
            controller.empty_input()
            return;

        #If we're walking, stop for a frame
        #Also, if we're shielding, don't try to dash. We will accidentally roll
        if smashbot_state.action == melee.Action.WALK_SLOW or \
            smashbot_state.action == melee.Action.WALK_MIDDLE or \
            smashbot_state.action == melee.Action.WALK_FAST or \
            smashbot_state.action == melee.Action.SHIELD_START or \
            smashbot_state.action == melee.Action.SHIELD_REFLECT or \
            smashbot_state.action == melee.Action.SHIELD:
                controller.empty_input()
                return;

        #If we're starting the turn around animation, keep pressing that way or
        #   else we'll get stuck in the slow turnaround
        if smashbot_state.action == melee.Action.TURNING and smashbot_state.action_frame == 1:
            return;

        #Dash back, since we're about to start running
        # #melee.Action.FOX_DASH_FRAMES
        if smashbot_state.action == melee.Action.DASHING and smashbot_state.action_frame >= 11:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5);
                return;

        #We can't dash IMMEDIATELY after landing. So just chill for a bit
        if (smashbot_state.action == melee.Action.LANDING and smashbot_state.action_frame < 2) or \
            not smashbot_state.on_ground:
                controller.empty_input();
                return;

        #Don't run off the stage
        if abs(smashbot_state.x) > \
            melee.stages.edgegroundposition(gamestate.stage) - 6.6:#(3 * FOX_DASH_SPEED):
                x = 0
                if smashbot_state.x < 0:
                    x = 1
                controller.tilt_analog(melee.Button.BUTTON_MAIN, x, .5);
                return;

        #Are we outside the given radius of dash dancing?
        if smashbot_state.x < self.pivotpoint - self.radius:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5);
            return;

        if smashbot_state.x > self.pivotpoint + self.radius:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5);
            return;

        #Keep running the direction we're going
        controller.tilt_analog(melee.Button.BUTTON_MAIN, int(not smashbot_state.facing), .5);
        return;
