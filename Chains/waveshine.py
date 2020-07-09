import melee
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

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        shineablestates = [Action.TURNING, Action.STANDING, Action.WALK_SLOW, Action.WALK_MIDDLE, \
            Action.WALK_FAST, Action.EDGE_TEETERING_START, Action.EDGE_TEETERING, Action.CROUCHING, \
            Action.RUNNING, Action.RUN_BRAKE, Action.CROUCH_START, Action.CROUCH_END] # Added last 3 because Smashbot would do nothing if Chains.Waveshine was called during them

        jcshine = (smashbot_state.action == Action.KNEE_BEND) and (smashbot_state.action_frame == 3)
        lastdashframe = (smashbot_state.action == Action.DASHING) and (smashbot_state.action_frame == 12)

        # If somehow we are off stage, give up immediately
        if smashbot_state.off_stage:
            self.interruptible = True
            controller.empty_input()
            return

        # Shine clank! We should shine again if we're in range
        if not opponent_state.hitlag and opponent_state.hitstun_frames_left == 0 and \
                smashbot_state.action == Action.SWORD_DANCE_2_MID_AIR and \
                gamestate.distance < 11.8:
            self.hasshined = False

        # Do the shine if we can
        if not self.hasshined and ((smashbot_state.action in shineablestates) or lastdashframe or jcshine):
            self.interruptible = False
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            self.hasshined = True
            return

        # If we're in the early knee bend frames, just hang on and wait
        if (smashbot_state.action == Action.KNEE_BEND) and (smashbot_state.action_frame < 3):
            controller.empty_input()
            return

        # Pivot. You can't shine from a dash animation. So make it a pivot
        if smashbot_state.action == Action.DASHING:
            # Turn around
            self.interruptible = True
            controller.release_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, int(not smashbot_state.facing), .5)
            #controller.press_button(Button.BUTTON_Y) #attempt JC shine instead of pivot shine
            return

        # In the off-chance waveshine.py gets called during GRAB_WAIT, down-throw
        if smashbot_state.action == Action.GRAB_WAIT:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
            if self.controller.prev.main_stick[1] == 0:
                controller.empty_input()
            return

        isInShineStart = smashbot_state.action in [Action.DOWN_B_GROUND_START, Action.DOWN_B_GROUND]
        needsJC = smashbot_state.action in [Action.SHIELD_RELEASE, Action.SHIELD, Action.TURNING_RUN] #Added TURNING_RUN in case waveshine gets called during that animation

        # Jump out of shield, turning run, or tilt turn
        if needsJC or (smashbot_state.action == Action.TURNING and smashbot_state.action_frame in range(2,12)): #
            if controller.prev.button[Button.BUTTON_Y]:
                controller.empty_input()
                return
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Jump out of shine
        if isInShineStart:
            self.interruptible = False
            if smashbot_state.action_frame >= 3:
                controller.press_button(Button.BUTTON_Y)
                return
            else:
                controller.empty_input()
                return

        # We shouldn't need these. It's just there in case we miss the knee bend somehow
        jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]

        # Airdodge back down into the stage
        if jcshine or smashbot_state.action in jumping:
            self.interruptible = False
            controller.press_button(Button.BUTTON_L)
            # Always wavedash the direction opponent is moving
            opponentspeed = opponent_state.speed_x_attack + opponent_state.speed_ground_x_self
            direction = opponentspeed > 0
            onleft = smashbot_state.x < opponent_state.x
            if abs(opponentspeed) < 0.01:
                direction = onleft

            # Unless we're RIGHT on top of the edge. In which case the only safe wavedash is back on the stage
            edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
            if opponent_state.x < 0:
                edge_x = -edge_x
            edgedistance = abs(edge_x - smashbot_state.x)
            if edgedistance < 0.5:
                direction = smashbot_state.x < 0

            # If we're facing the edge, it's not safe to wavedash off the edge. Adjust the distance down
            if smashbot_state.facing == smashbot_state.x > 0:
                distance = max(edgedistance / 15, 1)

            # Normalize distance from (0->1) to (-0.5 -> 0.5)
            delta = (self.distance / 2) # 0->0.5
            if not direction:
                delta = -delta
            controller.tilt_analog(Button.BUTTON_MAIN, 0.5 + delta, .35)
            return

        # If we're sliding and have shined, then we're all done here
        if smashbot_state.action == Action.LANDING_SPECIAL: #removed and self.hasshined
            self.interruptible = True
            controller.empty_input()
            return

        if smashbot_state.action in [Action.SWORD_DANCE_4_MID_AIR, Action.SWORD_DANCE_4_LOW_AIR]:
            self.interruptible = False
        else:
            self.interruptible = True

        controller.empty_input()
