#!/usr/bin/python3
from util import memorywatcher, paths, gamestate, controller, enums
import sys
import argparse

parser = argparse.ArgumentParser(description='SmashBot: The AI that beats you at Melee')
parser.add_argument('--port', '-p', type=int,
                    help='The controller port SmashBot will play on',
                    default=2)

args = parser.parse_args()

#Setup some config files before we can really play
paths.first_time_setup()
paths.configure_controller_settings(args.port)

memory_watcher = memorywatcher.MemoryWatcher()
game_state = gamestate.GameState()
controller = controller.Controller()

#"Main loop" of SmashBot, process memory updates until the frame has incremented
for mem_update in memory_watcher:
    if game_state.update(mem_update):
        #TODO: The frame has incremented, process it!
        print(game_state)
        if game_state.menu_state == enums.Menu.IN_GAME:
            if game_state.frame % 2:
                controller.press_button(enums.Button.BUTTON_A)
            else:
                controller.release_button(enums.Button.BUTTON_A)
