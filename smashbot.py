#!/usr/bin/python3
import numpy as np
import gym
import melee
import argparse
import signal
import sys
import util

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
                    default=False)
parser.add_argument('--movie', '-m',
                    help='Train SmashBot using a DTM movie',
                    default=None)
parser.add_argument('--iso', '-i',
                    help='ISO file of Melee',
                    default=None)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

opponent_type = melee.enums.ControllerType.UNPLUGGED

#Create our Dolphin object. This will be the primary object that we will interface with
dolphin = melee.dolphin.Dolphin(ai_port=args.port, opponent_port=args.opponent,
    opponent_type=opponent_type, logger=log)

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

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
dolphin.run(render=True, movie_path=args.movie, iso_path=args.iso)
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

#Train from a movie file
# NOTE: Don't actually press any buttons here. The game will play itself from the DTM
# file, so just sit back and watch.
if args.movie != None:
    dtmfile = melee.dtmreader.DTMReader(args.movie)

    #Play the movie back, frame by frame
    i = 0
    for actions in dtmfile:
        #WiiU adapters poll really fast, and contain 8x the number of inputs we actually want
        #So here we have to discard inputs except multiples of 8
        i += 1
        if i % 7 != 0:
            continue
        #Ignore the first bunch of frames of input
        if i < 337 * 7:
            continue

        state_prev = gamestate.tolist()
        #Progress the environment one frame
        gamestate.step()
        state = gamestate.tolist()

        action_state = actions[args.port]
        action = util.action_toint(action_state)
        #TODO: Fix action state not syncing with playback
        for butt in action_state.button:
            if action_state.button[butt]:
                print("\t"  + str(butt))
                last_button_frame = i

        print(gamestate.frame, gamestate.ai_state.action, gamestate.ai_state.coin_down)

        continue

        #Only bother with any logic if we're in a game, otherwise just go to the next frame
        if gamestate.menu_state == melee.enums.Menu.IN_GAME:
            #Get button presses from DTM. They are handed down as dicts of each controller's
            # inputs for this frame
            #But for this, we only care about OUR inputs
            action_state = actions[args.port]
            action = util.action_toint(action_state)

            #TODO: Fix action state not syncing with playback
            import time
            time.sleep(.05)
            print(i, action_state.button)
            for butt in action_state.button:
                if action_state.button[butt]:
                    print(butt)
            print(gamestate.ai_state.action)

            #Calculate score/reward
            scorestate.update(gamestate)
            score_new = scorestate.score()
            reward = score_new - score
            score = score_new

            agent.train(state, action, state_prev, reward)

        #If we're in the first frame of the postgame menu, then we must have
        #   just finished a match!
        elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
            if gamestate.frame == 1:
                print("Saving...")
                agent.save(filename)

    #TODO: Let's make this more elegant, shall we?
    agent.save(filename)
    sys.exit(0)

state_prev = None
#Main loop: process memory updates until the frame has incremented
while True:
    gamestate.step()
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
        x, y, button = util.action_to_presses(action)
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
