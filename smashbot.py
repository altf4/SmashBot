#!/usr/bin/python3
import argparse
import os
import signal
import sys
import socket 
import fcntl
import errno
import random
import posix

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

# Plug our controller in
print("Connecting to TASTM32...")
controller_one.connect()
print("Connected")

print("Setting up CrowdControl listener...")
cc_path = "crowdcontrol_socket.fifo"
try:
    os.mkfifo(cc_path)
except Exception as ex:
    pass
    
ccSocket = posix.open(cc_path, posix.O_RDWR|posix.O_NONBLOCK)
print("Establshed")


RANDOM_STAGES = [melee.Stage.FINAL_DESTINATION,
                melee.Stage.BATTLEFIELD,
                melee.Stage.POKEMON_STADIUM,
                melee.Stage.DREAMLAND,
                melee.Stage.YOSHIS_STORY]
randomstage = random.choice(RANDOM_STAGES)

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step()
    if log:
        log.log("Notes", "Processing Time: "  + str(console.processingtime * 1000) + "ms")

    # What menu are we in?
    if gamestate.menu_state == melee.Menu.IN_GAME:
        # This can happen when using the crowd control ASM codes.
        if gamestate.frame < -500:
            continue

        # Crowd Control queue management. Tell the spawner if an item spawned
        if len(gamestate.projectiles) >= 10:
            posix.write(ccSocket, b'\xFF')
        else:
            for item in gamestate.projectiles:
                if item.frame >= 1399:
                    posix.write(ccSocket, item.type.value.to_bytes(1, 'big'))

        try:
            agent1.act(gamestate)

        except Exception as error:
            # Do nothing in case of error thrown!
            agent1.controller.empty_input()

            if log:
                log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
            else:
                print("WARNING: Exception thrown: ", error)
        if log:
            log.log("Notes", "Goals: " + str(agent1.strategy), concat=True)
            log.logframe(gamestate)
            log.writeframe()
    else:
        # Reroll the random stage each new menu
        if gamestate.frame == 0:
            randomstage = random.choice(RANDOM_STAGES)

        melee.menuhelper.MenuHelper.menu_helper_simple(gamestate,
                                                        controller_one,
                                                        melee.Character.FOX,
                                                        randomstage,
                                                        autostart=False,
                                                        swag=True)
