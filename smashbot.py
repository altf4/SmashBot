#!/usr/bin/python3
from util import memorywatcher, paths, gamestate, controller, enums
from goals import choosecharacter

import argparse
import globals

goal = None

def creategoal(new_goal):
    global goal
    if goal == None:
        goal = new_goal()
    if type(goal) !=  new_goal:
        goal = new_goal()

parser = argparse.ArgumentParser(description='SmashBot: The AI that beats you at Melee')
parser.add_argument('--port', '-p', type=int,
                    help='The controller port SmashBot will play on',
                    default=2)
parser.add_argument('--opponent', '-o', type=int,
                    help='The controller port the human will play on',
                    default=1)

args = parser.parse_args()

#Setup some config files before we can really play
paths.first_time_setup()
paths.configure_controller_settings(args.port)
globals.init(args.port, args.opponent)

memory_watcher = memorywatcher.MemoryWatcher()

game_state = globals.gamestate
controller = globals.controller

#"Main loop" of SmashBot, process memory updates until the frame has incremented
for mem_update in memory_watcher:
    if game_state.update(mem_update):
        #TODO: The frame has incremented, process it!
        #print(game_state)
        if game_state.menu_state == enums.Menu.IN_GAME:
            if game_state.frame % 2:
                controller.press_button(enums.Button.BUTTON_A)
            else:
                controller.release_button(enums.Button.BUTTON_A)
        elif game_state.menu_state == enums.Menu.CHARACTER_SELECT:
            creategoal(choosecharacter.ChooseCharacter)
            goal.pickstrategy()

        #Flush and button presses queued up
        controller.flush()
