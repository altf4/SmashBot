#!/usr/bin/python3
import numpy as np
import gym
import melee
import argparse
import signal
import sys

from agent import Agent
from scorestate import ScoreState

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
         raise argparse.ArgumentTypeError("%s is an invalid controller port. \
         Must be 1, 2, 3, or 4." % value)
    return ivalue

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--live', '-l',
                    help='The opponent playing live with a GCN Adapter',
                    default=True)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

#Create our Dolphin object. This will be the primary object that we will interface with
dolphin = melee.dolphin.Dolphin(ai_port=args.port, opponent_port=args.opponent,
    live=args.live, logger=log)
#Create our GameState object for the dolphin instance
gamestate = melee.gamestate.GameState(dolphin)
#Create our Controller object that we can press buttons on
controller = melee.controller.Controller(port=args.port, dolphin=dolphin)

def signal_handler(signal, frame):
    dolphin.terminate()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

#Output layer dimension
#6 for buttons
#two options of 7 stick levels for the main stick
action_dim = 6 * 7 * 7

"""Modlate a number from 0-action_dim into discrete button presses"""
#TODO: Verify this better
def action_to_presses(action):
    button_int = action % 6
    button = None
    if button_int == 0:
        button = melee.enums.Button.BUTTON_A
    if button_int == 1:
        button = melee.enums.Button.BUTTON_B
    if button_int == 2:
        button = melee.enums.Button.BUTTON_L
    if button_int == 3:
        button = melee.enums.Button.BUTTON_Y
    if button_int == 4:
        button = melee.enums.Button.BUTTON_Z
    if button_int == 5:
        button = None

    x_int = (action // 6) % 7
    x = 0.5
    if x_int == 0:
        x = 0
    if x_int == 1:
        x = 0.2
    if x_int == 2:
        x = 0.4
    if x_int == 3:
        x = 0.5
    if x_int == 4:
        x = 0.6
    if x_int == 5:
        x = 0.8
    if x_int == 6:
        x = 1

    y_int = (action // (6*7)) % 7
    y = 0.5
    if y_int == 0:
        y = 0
    if y_int == 1:
        y = 0.2
    if y_int == 2:
        y = 0.4
    if y_int == 3:
        y = 0.5
    if y_int == 4:
        y = 0.6
    if y_int == 5:
        y = 0.8
    if y_int == 6:
        y = 1

    return x, y, button

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
dolphin.run(render=False)
#Plug our controller in
controller.connect()

gamestate_dim = len(gamestate.tolist())

score = 0
match_count = 1
max_matches = 5

scorestate = ScoreState()
filename = "testing.model"

agent = Agent(gamestate_dim, action_dim)
try:
    agent.load(filename)
except OSError:
    pass

state_prev = None
#Main loop: process memory updates until the frame has incremented
for mem_update in gamestate:
    #If the frame counter has updated, then process it!
    if gamestate.update(mem_update):
        #What menu are we in?
        if gamestate.menu_state == melee.enums.Menu.IN_GAME:
            #Calculate score/reward
            scorestate.update(gamestate)
            score_new = scorestate.score()
            reward = score_new - score
            score = score_new

            #Get the current gamestate as a usable list object
            state = gamestate.tolist()

            #What action does the model want us to take?
            action = agent.act(state)

            #perform the action on the controller
            x, y, button = action_to_presses(action)
            controller.simple_press(x, y, button)

            #Train! (unless it's the first frame)
            if state_prev != None:
                agent.train(state, action, state_prev, reward)

            #Keep track of the last state
            state_prev = state

        #If we're at the character select screen, choose our character
        elif gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT:
            if gamestate.opponent_state.controller_status != melee.enums.ControllerStatus.CONTROLLER_CPU or \
                gamestate.opponent_state.character != melee.enums.Character.MARTH:
                melee.menuhelper.changecontrollerstatus(gamestate=gamestate, controller=controller,
                    port=args.opponent, status=melee.enums.ControllerStatus.CONTROLLER_CPU,
                    character=melee.enums.Character.MARTH)
            else:
                melee.menuhelper.choosecharacter(character=melee.enums.Character.JIGGLYPUFF,
                    gamestate=gamestate, controller=controller, start=True)
        #If we're at the postgame scores screen, spam START
        elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
            melee.menuhelper.skippostgame(controller=controller)
            #If we're in the first frame of the postgame menu, then we must have
            #   just finished a match!
            if gamestate.frame == 1:
                print("{} - {}".format(match_count, score))
                print("\t", agent.epsilon)
                agent.save(filename)
                match_count += 1
                score = 0
        #If we're at the stage select screen, choose a stage
        elif gamestate.menu_state == melee.enums.Menu.STAGE_SELECT:
            melee.menuhelper.choosestage(stage=melee.enums.Stage.BATTLEFIELD,
                gamestate=gamestate, controller=controller)
        #Flush any button presses queued up
        controller.flush()
        if log:
            log.logframe(gamestate)
            log.writeframe()
