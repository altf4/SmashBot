#!/usr/bin/python3
import argparse
import os
import signal
import sys
import time

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
parser.add_argument('--difficulty', '-i', type=int,
                    help='Manually specify difficulty level of SmashBot')
parser.add_argument('--nodolphin', '-n', action='store_true',
                    help='Don\'t run dolphin, (it is already running))')
parser.add_argument('--dolphinexecutable', '-e', type=is_dir,
                    help='Manually specify Dolphin executable')
parser.add_argument('--configdir', '-c', type=is_dir,
                    help='Manually specify the Dolphin config directory to use')
parser.add_argument('--address', '-a', default="",
                    help='IP address of Slippi/Wii')
parser.add_argument('--connect_code', '-t', default="",
                    help='Direct connect code to connect to in Slippi Online')

args = parser.parse_args()

log = None
if args.debug:
    log = melee.logger.Logger()

#Options here are:
#   GCN_ADAPTER will use your WiiU adapter for live human-controlled play
#   UNPLUGGED is pretty obvious what it means
#   STANDARD is a named pipe input (bot)
opponent_type = melee.enums.ControllerType.STANDARD
if not args.bot:
    opponent_type = melee.enums.ControllerType.GCN_ADAPTER

#Create our console object. This will be the primary object that we will interface with
console = melee.console.Console(path=args.dolphinexecutable,
                                slippi_address=args.address,
                                logger=log)

controller_one = melee.controller.Controller(console=console, port=args.port)
controller_two = melee.controller.Controller(console=console,
                                             port=args.opponent,
                                             type=opponent_type)

#initialize our agent
agent1 = ESAgent(console, args.port, args.opponent, controller_one)
agent2 = None
if args.bot:
    controller_two = melee.controller.Controller(console=console, port=args.opponent)
    agent2 = ESAgent(console, args.opponent, args.port, controller_two)

def signal_handler(signal, frame):
    console.stop()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
if not args.nodolphin:
    console.run()
    time.sleep(1)


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
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH]

#Main loop
while True:
    #"step" to the next frame
    gamestate = console.step()

    #What menu are we in?
    if gamestate.menu_state == melee.enums.Menu.IN_GAME:
        #The agent's "step" will cascade all the way down the objective hierarchy
        if args.difficulty:
            agent1.difficulty = int(args.difficulty)
            if agent2:
                agent2.difficulty = int(args.difficulty)
        else:
            agent1.difficulty = gamestate.player[agent1.smashbot_port].stock
            if agent2:
                agent2.difficulty = gamestate.player[agent2.smashbot_port].stock

        if gamestate.player[agent1.smashbot_port].character not in supportedcharacters:
            melee.techskill.multishine(ai_state=gamestate.player[agent1.smashbot_port],
                                       controller=agent1.controller)
        else:
            # try:
            discovered_port = melee.gamestate.port_detector(gamestate, agent1.controller, melee.enums.Character.FOX)
            agent1.smashbot_port = discovered_port
            if agent1.smashbot_port == 1:
                agent1.opponent_port = 2
            else:
                agent1.opponent_port = 1

            agent1.act(gamestate)
            if agent2:
                agent2.act(gamestate)
            # except Exception as error:
            #     # Do nothing in case of error thrown!
            #     agent1.controller.empty_input()
            #     if agent2:
            #         agent2.controller.empty_input()
            #     if log:
            #         log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)
            #     else:
            #         print("WARNING: Exception thrown: ", error)
    else:
        melee.menuhelper.MenuHelper.menu_helper_simple(gamestate,
                                                        controller_one,
                                                        args.port,
                                                        melee.enums.Character.FOX,
                                                        melee.enums.Stage.FINAL_DESTINATION,
                                                        args.connect_code,
                                                        autostart=False,
                                                        swag=True)

    if log:
        log.log("Notes", "Goals: " + str(agent1.strategy), concat=True)
        log.logframe(gamestate)
        log.writeframe()
