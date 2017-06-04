import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# Shine, then wavedash
class Waveshine(Chain):
    # Distance argument is a multiplier to how far we'll wavedash
    # 0 is straight in place
    # 1 is max distance
    def __init__(self, distance=1):
        self.hasshined = False
        self.distance = distance

    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING]

        jcshine = (smashbot_state.action == Action.KNEE_BEND) and (smashbot_state.action_frame == 3)
        lastdashframe = (smashbot_state.action == Action.DASHING) and (smashbot_state.action_frame == 12)

        # Do the shine if we can
        if not self.hasshined and ((smashbot_state.action in shineablestates) or lastdashframe):
            self.interruptible = False
            controller.press_button(Button.BUTTON_B);
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0);
            self.hasshined = True
            return

        # Pivot. You can't shine from a dash animation. So make it a pivot
        if smashbot_state.action == Action.DASHING:
            # Turn around
            self.interruptible = True
            controller.release_button(Button.BUTTON_B);
            controller.tilt_analog(Button.BUTTON_MAIN, int(not smashbot_state.facing), .5);
            return;

        isInShineStart = (smashbot_state.action == Action.DOWN_B_STUN or \
            smashbot_state.action == Action.DOWN_B_GROUND_START or \
            smashbot_state.action == Action.DOWN_B_GROUND)

        # Jump out of shine
        if isInShineStart and smashbot_state.action_frame >= 3 and smashbot_state.on_ground:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # We shouldn't need these. It's just there in case we miss the knee bend somehow
        jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]

        # Airdodge back down into the stage
        #TODO: Avoid going off the edge
        if jcshine or smashbot_state.action in jumping:
            self.interruptible = False
            controller.press_button(Button.BUTTON_L)
            # Always wavedash toward opponent
            onleft = smashbot_state.x < opponent_state.x
            # Normalize distance to be .5 -> 1
            x = (self.distance + 0.5) / 2
            if not onleft:
                x = -x
            controller.tilt_analog(Button.BUTTON_MAIN, x, .2);
            return

        # If we're sliding and have shined, then we're all done here
        if smashbot_state.action == Action.LANDING_SPECIAL and self.hasshined:
            self.interruptible = True
            controller.empty_input()
            return

        if smashbot_state.action == Action.STANDING:
            self.interruptible = True

        controller.empty_input()
