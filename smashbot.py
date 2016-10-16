#!/usr/bin/python3
from util import memorywatcher, paths, gamestate, controller, enums, logger
#TODO: Make this auto-import all new chains
from chains import choosecharacter, multishine, skippostgame

import argparse
import globals
import signal
import sys

def check_port(value):
    ivalue = int(value)
    if ivalue < 1 or ivalue > 4:
         raise argparse.ArgumentTypeError("%s is an invalid controller port. Must be 1, 2, 3, or 4." % value)
    return ivalue

chain = None

parser = argparse.ArgumentParser(description='SmashBot: The AI that beats you at Melee')
parser.add_argument('--port', '-p', type=check_port,
                    help='The controller port SmashBot will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=check_port,
                    help='The controller port the human will play on',
                    default=1)
parser.add_argument('--debug', '-d', action='store_true',
                    help='Debug mode. Creates a CSV of all game state')

args = parser.parse_args()

#Setup some config files before we can really play
paths.first_time_setup(args.port)
paths.configure_controller_settings(args.port)
globals.init(args.port, args.opponent)
log = globals.log

def signal_handler(signal, frame):
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
        sys.exit(0)

def createchain(new_chain):
    global chain
    if chain == None:
        chain = new_chain()
    if type(chain) !=  new_chain:
        chain = new_chain()

if args.debug:
    signal.signal(signal.SIGINT, signal_handler)

memory_watcher = memorywatcher.MemoryWatcher()

game_state = globals.gamestate
controller = globals.controller

#"Main loop" of SmashBot, process memory updates until the frame has incremented
for mem_update in memory_watcher:
    #If the frame counter has updated, then process it!
    if game_state.update(mem_update):
        if game_state.menu_state == enums.Menu.IN_GAME:
            createchain(multishine.MultiShine)
            chain.pressbuttons()
        elif game_state.menu_state == enums.Menu.CHARACTER_SELECT:
            createchain(choosecharacter.ChooseCharacter)
            chain.pressbuttons()
        elif game_state.menu_state == enums.Menu.POSTGAME_SCORES:
            createchain(skippostgame.SkipPostgame)
            chain.pressbuttons()
        #Flush and button presses queued up
        controller.flush()
        if args.debug:
            log.logframe()
            log.writeframe()
