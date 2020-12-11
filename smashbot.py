#!/usr/bin/python3
import argparse
import os
import signal
import sys

import melee

from esagent import ESAgent

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
parser.add_argument('--dolphinexecutable', '-e', type=is_dir,
                    help='Manually specify Dolphin executable')
parser.add_argument('--stage', '-s', default="FD",
                    help='Specify which stage to select')

stagedict = {
    "FD": melee.enums.Stage.FINAL_DESTINATION,
    "BF": melee.enums.Stage.BATTLEFIELD,
    "YS": melee.enums.Stage.YOSHIS_STORY,
    "FOD": melee.enums.Stage.FOUNTAIN_OF_DREAMS,
    "DL": melee.enums.Stage.DREAMLAND,
    "PS": melee.enums.Stage.POKEMON_STADIUM
}

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

# Options here are:
#    GCN_ADAPTER will use your WiiU adapter for live human-controlled play
#    UNPLUGGED is pretty obvious what it means
#    STANDARD is a named pipe input (bot)
opponent_type = melee.enums.ControllerType.STANDARD
if not args.bot:
    opponent_type = melee.enums.ControllerType.GCN_ADAPTER

# Create our console object. This will be the primary object that we will interface with
console = melee.console.Console(path=args.dolphinexecutable,
                                logger=log)

controller_one = melee.controller.Controller(console=console, port=args.port)
controller_two = melee.controller.Controller(console=console,
                                             port=args.opponent,
                                             type=opponent_type)

# initialize our agent
agent1 = ESAgent(console, args.port, args.opponent, controller_one, args.difficulty)
agent2 = None
if args.bot:
    controller_two = melee.controller.Controller(console=console, port=args.opponent)
    agent2 = ESAgent(console, args.opponent, args.port, controller_two, args.difficulty)

def signal_handler(signal, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("") # because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Run dolphin
console.run()

# Connect to the console
print("Connecting to console...")
if not console.connect():
    print("ERROR: Failed to connect to the console.")
    print("\tIf you're trying to autodiscover, local firewall settings can " +
          "get in the way. Try specifying the address manually.")
    sys.exit(-1)
print("Connected")

# Plug our controller in
controller_one.connect()
controller_two.connect()

supportedcharacters = [melee.enums.Character.PEACH, melee.enums.Character.CPTFALCON, melee.enums.Character.FALCO, \
    melee.enums.Character.FOX, melee.enums.Character.SAMUS, melee.enums.Character.ZELDA, melee.enums.Character.SHEIK, \
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH, melee.enums.Character.GANONDORF]

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step()

    # What menu are we in?
    if gamestate.menu_state == melee.enums.Menu.IN_GAME:
        try:
            agent1.act(gamestate)
            if agent2:
                agent2.act(gamestate)
        except Exception as error:
            # Do nothing in case of error thrown!
            agent1.controller.empty_input()
            if agent2:
                agent2.controller.empty_input()
            if log:
                log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
            else:
                print("WARNING: Exception thrown: ", error)
    else:
        melee.menuhelper.MenuHelper.menu_helper_simple(gamestate,
                                                        controller_one,
                                                        melee.enums.Character.FOX,
                                                        stagedict.get(args.stage, melee.enums.Stage.FINAL_DESTINATION),
                                                        connect_code="",
                                                        autostart=False,
                                                        swag=True)

    if log:
        log.log("Notes", "Goals: " + str(agent1.strategy), concat=True)
        log.logframe(gamestate)
        log.writeframe()
