#!/usr/bin/python3
import argparse
import os
import signal
import sys

import melee
import dtm
from melee import controller

from esagent import ESAgent

import threading
import queue

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
        raise argparse.ArgumentTypeError("%s is an invalid controller port. \
        Must be 1, 2, 3, or 4." % value)
    return ivalue

def is_dir(dirname):
    """Checks if a path is an actual directory"""
    if not os.path.isdir(dirname):
        msg = "{0} is not a directory".format(dirname)
        raise argparse.ArgumentTypeError(msg)
    else:
        return dirname

parser = argparse.ArgumentParser(description='Example of libmelee in action')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port your AI will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the opponent will play on',
                    default=1)
parser.add_argument('--bot', '-b',
                    help='Opponent is a second instance of SmashBot',
                    default=False)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')
parser.add_argument('--difficulty', '-i', type=int, default=-1,
                    help='Manually specify difficulty level of SmashBot')
parser.add_argument('--stage', '-s', default="FD",
                    help='Specify which stage to select')
parser.add_argument('--teams', '-a',
                    help='Play a game of teams against two SmashBots',
                    action='store_true')
stagedict = {
    "FD": melee.Stage.FINAL_DESTINATION,
    "BF": melee.Stage.BATTLEFIELD,
    "YS": melee.Stage.YOSHIS_STORY,
    "FOD": melee.Stage.FOUNTAIN_OF_DREAMS,
    "DL": melee.Stage.DREAMLAND,
    "PS": melee.Stage.POKEMON_STADIUM
}

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()


# Create our console object. This will be the primary object that we will interface with
console = melee.Console(path=None,
                        system="gamecube",
                        copy_home_directory=False,
                        logger=log)

controller_one = melee.Controller(console=console,
                              port=args.port,
                              serial_device="/dev/ttyACM0",
                              type=melee.ControllerType.STANDARD)

# initialize our agent
agent1 = ESAgent(console, args.port, args.opponent, controller_one, args.difficulty)

def signal_handler(signal, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("") # because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Connect to the console
print("Connecting to console...")
if not console.connect():
    print("ERROR: Failed to connect to the console.")
    sys.exit(-1)
print("Connected")

def naviate_to_allstar(gamestate, controller):
    """Given a gamestate, press buttons on controller to get us into allstar

    Luigi, very hard
    """
    if gamestate.frame % 2 == 0 and gamestate.menu_state != melee.Menu.UNKNOWN_MENU:
        controller.empty_input()
        return

    if gamestate.menu_state == melee.Menu.PRESS_START:
        controller.press_button(melee.Button.BUTTON_START)

    if gamestate.menu_state == melee.Menu.MAIN_MENU:
        # First submenu
        if gamestate.submenu == melee.SubMenu.MAIN_MENU_SUBMENU:
            if gamestate.menu_selection == 0:
                controller.press_button(melee.Button.BUTTON_A)
            else:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
        # Second submenu
        if gamestate.submenu == melee.SubMenu.ONEP_MODE_SUBMENU:
            if gamestate.menu_selection == 0:
                controller.press_button(melee.Button.BUTTON_A)
            else:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
        # Third submenu
        if gamestate.submenu == melee.SubMenu.REGULAR_MATCH_SUBMENU:
            if gamestate.menu_selection == 2:
                controller.press_button(melee.Button.BUTTON_A)
            else:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
                
    # TODO: Fix this to actually read properly maybe
    if gamestate._menu_scene == 28677:     
        if gamestate.frame < 32:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 1)
        elif gamestate.frame < 42:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
        elif gamestate.frame < 55:
            controller.press_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 56:
            controller.release_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 78:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
        elif gamestate.frame < 91:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)            
        # 4 difficulty presses            
        elif gamestate.frame < 93:
            controller.press_button(melee.Button.BUTTON_A)
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, .5)            
        elif gamestate.frame < 94:
            controller.release_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 95:
            controller.press_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 96:
            controller.release_button(melee.Button.BUTTON_A)  
        elif gamestate.frame < 97:
            controller.press_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 98:
            controller.release_button(melee.Button.BUTTON_A)  
        elif gamestate.frame < 99:
            controller.press_button(melee.Button.BUTTON_A)
        elif gamestate.frame < 100:
            controller.release_button(melee.Button.BUTTON_A)  
        elif gamestate.frame > 120:
            controller.press_button(melee.Button.BUTTON_START)
        else:
            controller.empty_input()

with open("Initial_Inputs2.dtm", 'rb') as f:
    buffer_intitial = dtm.read_input(f.read())

with open("segment_1.dtm", 'rb') as f:
    buffer_allstar = dtm.read_input(f.read())

# Play setup dtm (triggers injection)
#agent1.controller.send_dtm(buffer_intitial)
t = threading.Thread(target=agent1.controller.send_dtm, args=(buffer_intitial,))
t.start()
t.join()

# Plug our controller in
print("Connecting to TASTM32...")
controller_one.connect()
print("Connected")

q = queue.Queue()
tasRunning = False

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step(tasRunning)
    #print(gamestate.menu_state, gamestate._menu_scene, gamestate.frame)
    # if 1 in gamestate.players:
    #     print(gamestate.players[1].position.x, gamestate.players[1].position.y)
    if log:
        log.log("Notes", "Processing Time: "  + str(console.processingtime * 1000) + "ms")

    # What menu are we in?
    if gamestate.menu_state == melee.Menu.IN_GAME:
        if gamestate.frame == -123:
            print("Queuing TAS inputs")
            t = threading.Thread(target=agent1.controller.send_dtm, args=(buffer_allstar, q))
            t.start() # start the tastm32 stuff in a new thread
            tasRunning = True
        elif gamestate.frame == -40:
            print("TAS begins!")
            q.put(1) # random message to unpause
            t.join()
            print("TAS Complete!")
        # try:
        #     agent1.act(gamestate)

        # except Exception as error:
        #     # Do nothing in case of error thrown!
        #     agent1.controller.empty_input()

        #     if log:
        #         log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
        #     else:
        #         print("WARNING: Exception thrown: ", error)
        # if log:
        #     log.log("Notes", "Goals: " + str(agent1.strategy), concat=True)
        #     log.logframe(gamestate)
        #     log.writeframe()
    else:
        naviate_to_allstar(gamestate, agent1.controller)
