import melee
import Tactics
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class SHIELD_ACTION(Enum): #consider adding possibilities for angled tilts and turnaround tilts
    PSSHINE = 0
    PSUTILT = 1
    PSDTILT = 2
    PSJAB = 3

class ShieldAction(Chain):
    def __init__(self, action=SHIELD_ACTION.PSSHINE):
        self.action = action

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        self.interruptible = True

        # Let go of A if we were already pressing A
        if controller.prev.button[Button.BUTTON_A]:
            controller.empty_input()
            return

        # Let go of B if we were already pressing B
        if controller.prev.button[Button.BUTTON_B]:
            controller.empty_input()
            return

        # Consider adding redundancy to check for SHIELD_RELEASE, but this just has button inputs atm
        if self.action == SHIELD_ACTION.PSSHINE:
            controller.press_button(Button.BUTTON_B)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, .3)
            return
        if self.action == SHIELD_ACTION.PSUTILT:
            controller.press_button(Button.BUTTON_A)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.7)
            return
        elif self.action == SHIELD_ACTION.PSDTILT:
            controller.press_button(Button.BUTTON_A)
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0.3)
            return
        elif self.action == SHIELD_ACTION.PSJAB:
            controller.press_button(Button.BUTTON_A)
            return


        #Do we need to jump cancel? #Jump canceling isn't valid for tilts
        #jumpcancelactions = [Action.SHIELD, Action.DASHING, Action.RUNNING]
        #if smashbot_state.action in jumpcancelactions:
            #self.interruptible = False
            #controller.press_button(Button.BUTTON_Y)
            #return

        # Jump out of shine #Jump canceling isn't valid for tilts
        #isInShineStart = (smashbot_state.action == Action.DOWN_B_STUN or \
            #smashbot_state.action == Action.DOWN_B_GROUND_START or \
            #smashbot_state.action == Action.DOWN_B_GROUND)
        #if isInShineStart and smashbot_state.action_frame >= 3 and smashbot_state.on_ground:
            #self.interruptible = False
            #controller.press_button(Button.BUTTON_Y)
            #return

        #this should not matter at all
        #if smashbot_state.action in [Action.FSMASH_MID, Action.UPSMASH, Action.DOWNSMASH]:
            # Are we in the early stages of the smash and need to charge?
            #if self.frames_charged < self.charge:
                #self.interruptible = False
                #self.frames_charged += 1
                #controller.press_button(Button.BUTTON_A)
                #return
            # Are we done with a smash and just need to quit?
            #else:
                 #self.interruptible = True
                 #controller.empty_input()
                 #return

        #We need to input a jump to wavedash out of these states if dash/run gets called while in one of these states, or else we get stuck
        #jcstates = [Action.DASHING]
        #if (smashbot_state.action in jcstates):
                #self.controller.press_button(Button.BUTTON_Y)
                #return

        # Airdodge for the wavedash
        #jumping = [Action.JUMPING_ARIAL_FORWARD, Action.JUMPING_ARIAL_BACKWARD]
        #jumpcancel = (smashbot_state.action == Action.KNEE_BEND) and (smashbot_state.action_frame == 3)
        #if jumpcancel or smashbot_state.action in jumping:
            #self.controller.press_button(Button.BUTTON_L)
            #onleft = smashbot_state.x < endposition #don't know how to call endposition here
            # Normalize distance from (0->1) to (0.5 -> 1)
            #x = 1
            #if onleft != True:
                #x = -x
            #self.controller.tilt_analog(Button.BUTTON_MAIN, x, 0.35)
            #return

        #Complete the pivot -- This block may be unnecessary if Fox can just tilt during Action.TURNING no matter what, he can't during tilt turn.
        #if smashbot_state.action == Action.TURNING:
            #controller.empty_input()
            #self.interruptible = True
            #return
