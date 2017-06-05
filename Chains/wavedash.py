import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# Wavedash
class Wavedash(Chain):
    # Distance argument is a multiplier to how far we'll wavedash
    # 0 is straight in place
    # 1 is max distance
    def __init__(self, distance=1):
        self.distance = distance

    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # We shouldn't need these. It's just there in case we miss the knee bend somehow
        jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]
        jumpcancel = (smashbot_state.action == Action.KNEE_BEND) and (smashbot_state.action_frame == 3)

        isInShineStart = smashbot_state.action in [Action.DOWN_B_STUN, Action.DOWN_B_GROUND_START, \
            Action.DOWN_B_GROUND]

        # Jump out of shine
        if isInShineStart and smashbot_state.action_frame >= 3 and smashbot_state.on_ground:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        shielding = smashbot_state.action in [Action.SHIELD_START, Action.SHIELD, \
            Action.SHIELD_RELEASE, Action.SHIELD_STUN, Action.SHIELD_REFLECT]
        neutral = smashbot_state.action in [Action.STANDING, Action.DASHING, \
            Action.RUNNING, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING]

        # Jump out of shield or neutral
        if shielding or neutral:
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Airdodge back down into the stage
        #TODO: Avoid going off the edge
        if jumpcancel or smashbot_state.action in jumping:
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
        if smashbot_state.action == Action.LANDING_SPECIAL:
            self.interruptible = True
            controller.empty_input()
            return

        if smashbot_state.action == Action.STANDING:
            self.interruptible = True

        controller.empty_input()
