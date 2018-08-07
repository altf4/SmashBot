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

def is_executable(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    msg = "{0} is not a directory".format(program)
    raise argparse.ArgumentTypeError(msg)

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
parser.add_argument('--dolphinexecutable', '-e', type=is_executable,
                    help='Manually specify Dolphin executable')
parser.add_argument('--configdir', '-c', type=is_dir,
                    help='Manually specify the Dolphin config directory to use')

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

#Create our Dolphin object. This will be the primary object that we will interface with
dolphin = melee.dolphin.Dolphin(ai_port=args.port,
                                opponent_port=args.opponent,
                                opponent_type=opponent_type,
                                logger=log)

gamestate = melee.gamestate.GameState(dolphin)

#initialize our agent
agent1 = ESAgent(dolphin, gamestate, args.port, args.opponent)
agent2 = None
if args.bot:
    agent2 = ESAgent(dolphin, gamestate, args.opponent, args.port)

def signal_handler(signal, frame):
    dolphin.terminate()
    if args.debug:
        log.writelog()
        print("") #because the ^C will be on the terminal
        print("Log file created: " + log.filename)
    print("Shutting down cleanly...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Run dolphin and render the output
if not args.nodolphin:
    dolphin.run(render=True, dolphin_executable_path=args.dolphinexecutable, dolphin_config_path=args.configdir)

#Plug our controller in
#   Due to how named pipes work, this has to come AFTER running dolphin
#   NOTE: If you're loading a movie file, don't connect the controller,
#   dolphin will hang waiting for input and never receive it
agent1.controller.connect()
if agent2:
    agent2.controller.connect()

supportedcharacters = [melee.enums.Character.PEACH, melee.enums.Character.CPTFALCON, melee.enums.Character.FALCO, \
    melee.enums.Character.FOX, melee.enums.Character.SAMUS, melee.enums.Character.ZELDA, melee.enums.Character.SHEIK, \
    melee.enums.Character.PIKACHU, melee.enums.Character.JIGGLYPUFF, melee.enums.Character.MARTH]

#Main loop
while True:
    #"step" to the next frame
    gamestate.step()

    #What menu are we in?
    if gamestate.menu_state == melee.enums.Menu.IN_GAME:
        #The agent's "step" will cascade all the way down the objective hierarchy
        if args.difficulty:
            agent1.difficulty = int(args.difficulty)
            if agent2:
                agent2.difficulty = int(args.difficulty)
        else:
            agent1.difficulty = agent1.smashbot_state.stock
            if agent2:
                agent2.difficulty = agent2.smashbot_state.stock

        if gamestate.stage != melee.enums.Stage.FINAL_DESTINATION:
            melee.techskill.multishine(ai_state=agent1.smashbot_state, controller=agent1.controller)
        elif agent1.opponent_state.character not in supportedcharacters:
            melee.techskill.multishine(ai_state=agent1.smashbot_state, controller=agent1.controller)
        else:
            try:
                agent1.act()
                if agent2:
                    agent2.act()
            except Exception as error:
                # Do nothing in case of error thrown!
                controller.empty_input()
                if log:
                    log.log("Notes", "Exception thrown: " + repr(error) + " ", concat=True)

    #If we're at the character select screen, choose our character
    elif gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT:
        melee.menuhelper.choosecharacter(character=melee.enums.Character.FOX,
                                        gamestate=gamestate,
                                        port=args.port,
                                        opponent_port=args.opponent,
                                        controller=agent1.controller,
                                        swag=True,
                                        start=False)
        if agent2:
            melee.menuhelper.choosecharacter(character=melee.enums.Character.FOX,
                                            gamestate=gamestate,
                                            port=args.opponent,
                                            opponent_port=args.port,
                                            controller=agent2.controller,
                                            swag=True,
                                            start=False)
    #If we're at the postgame scores screen, spam START
    elif gamestate.menu_state == melee.enums.Menu.POSTGAME_SCORES:
        melee.menuhelper.skippostgame(controller=agent1.controller)
        if agent2:
            melee.menuhelper.skippostgame(controller=agent2.controller)
    #If we're at the stage select screen, choose a stage
    elif gamestate.menu_state == melee.enums.Menu.STAGE_SELECT:
        if agent2:
            agent2.controller.empty_input()
        melee.menuhelper.choosestage(stage=melee.enums.Stage.FINAL_DESTINATION,
                                    gamestate=gamestate,
                                    controller=agent1.controller)
    #Flush any button presses queued up
    agent1.controller.flush()
    if agent2:
        agent2.controller.flush()

    if log:
        log.log("Notes", "Goals: " + str(agent1.strategy), concat=True)
        log.logframe(gamestate)
        log.writeframe()
