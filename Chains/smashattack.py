import melee
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class SMASH_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2

class SmashAttack(Chain):
    def __init__(self, charge=0, direction=SMASH_DIRECTION.UP):
        self.charge = charge
        self.direction = direction
        self.frames_charged = 0

    def step(self, gamestate, smashbot_state, opponent_state):
        controller = self.controller

        if smashbot_state.action == Action.LANDING_SPECIAL:
            self.interruptible = True
            controller.empty_input()
            return

        # Do we need to jump cancel?
        jumpcancelactions = [Action.SHIELD, Action.SHIELD_RELEASE, Action.DASHING, Action.RUNNING]
        if smashbot_state.action in jumpcancelactions:
            if controller.prev.button[Button.BUTTON_Y]:
                controller.empty_input()
                return
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        # Jump out of shine
        isInShineStart = (smashbot_state.action == Action.DOWN_B_STUN or \
            smashbot_state.action == Action.DOWN_B_GROUND_START or \
            smashbot_state.action == Action.DOWN_B_GROUND)
        if isInShineStart and smashbot_state.action_frame >= 3 and smashbot_state.on_ground:
            if controller.prev.button[Button.BUTTON_Y]:
                controller.empty_input()
                return
            self.interruptible = False
            controller.press_button(Button.BUTTON_Y)
            return

        if smashbot_state.action in [Action.FSMASH_MID, Action.UPSMASH, Action.DOWNSMASH]:
            # Are we in the early stages of the smash and need to charge?
            if self.frames_charged < self.charge:
                self.interruptible = False
                self.frames_charged += 1
                controller.press_button(Button.BUTTON_A)
                return
            # Are we done with a smash and just need to quit?
            else:
                 self.interruptible = True
                 controller.empty_input()
                 return

        # Do the smash, unless we were already pressing A
        if controller.prev.button[Button.BUTTON_A]:
            controller.empty_input()
            self.interruptible = True
            return

        self.interruptible = False
        controller.press_button(Button.BUTTON_A)
        if self.direction == SMASH_DIRECTION.UP:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 1)
        elif self.direction == SMASH_DIRECTION.DOWN:
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)
        elif self.direction == SMASH_DIRECTION.FORWARD:
            controller.tilt_analog(Button.BUTTON_MAIN, int(smashbot_state.facing), .5)
