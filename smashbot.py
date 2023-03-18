#!/usr/bin/python3
import argparse
import os
import signal
import sys

import melee
import dtm
from melee import controller

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

pokefloats_finished = False

def navigate_to_pokefloats(gamestate, controller):
    if gamestate.menu_state == melee.Menu.STAGE_SELECT:
        # target is x=15.360001, y=-1.809998
        cursor = gamestate.players[1].cursor
        if cursor.y < -2.5:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, .8)
            return
        if cursor.y > -1.1:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, .2)
            return
        if cursor.x < 14.5:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .8, .5)
            return
        if cursor.x > 16.5:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .2, .5)
            return

        controller.press_button(melee.Button.BUTTON_A)
        return

    # Do the nametag glitch to play in pokefloats alone
    if gamestate.menu_state == melee.Menu.CHARACTER_SELECT:
        SETTINGS_MENU_HEIGHT = 20
        # Move to time and 4-minutes
        cursor_x, cursor_y = gamestate.players[1].cursor_x, gamestate.players[1].cursor_y
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame >= 45 and gamestate.frame <= 119:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 120:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 0, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame in [121, 122]:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 123:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 124:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 125:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 126:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 127:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 128:
            controller.empty_input()
            return
        # Turn items off
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 129:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 130:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 131:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 132:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 133:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 134:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 135:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 136:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 137:
            controller.press_button(melee.Button.BUTTON_A)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame <= 137 and gamestate.frame >= 164:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 165:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 1)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 166:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 167:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 168:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 169:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 170:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 171:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 172:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 173:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 174:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 175:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 176:
            controller.empty_input()
            return

        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 177:
            controller.press_button(melee.Button.BUTTON_B)
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame <= 178 and gamestate.frame >= 208:
            controller.empty_input()
            return
        if cursor_y > SETTINGS_MENU_HEIGHT and gamestate.frame == 209:
            controller.press_button(melee.Button.BUTTON_B)
            return

        print("stage B")
        if gamestate.frame >= 180 and gamestate.frame < 240:
            controller.empty_input()
            return
        if gamestate.frame in [241, 242, 243]:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 1)
            return
        if gamestate.frame == 244:
            controller.empty_input()
            return
        # Perform the nametag glitch
        if gamestate.frame == 245:
            controller.press_button(melee.Button.BUTTON_A)
            controller.press_button(melee.Button.BUTTON_B)
            return
        if gamestate.frame in [246, 247]:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 1)
            return
        if gamestate.frame >= 248 and gamestate.frame <= 275:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, .5)
            controller.release_button(melee.Button.BUTTON_A)
            controller.press_button(melee.Button.BUTTON_B)
            return
        if gamestate.frame == 276:
            controller.press_button(melee.Button.BUTTON_A)
            return
        if gamestate.frame >= 277:
            controller.empty_input()
            return

        # select character, go into game settings
        print("stage A", cursor_x, cursor_y)
        if gamestate.players[1].coin_down or cursor_y > 21:
            controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, 1)
            if cursor_y > 21:
                controller.press_button(melee.Button.BUTTON_A)
                print("GO INTO MENU")
            else:
                controller.release_button(melee.Button.BUTTON_A)
            return
        else:
            if gamestate.players[1].character == melee.Character.FOX:
                controller.press_button(melee.Button.BUTTON_A)
                return
            else:
                controller.release_button(melee.Button.BUTTON_A)
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .6, 1)
                return

        controller.empty_input()
        return

    if gamestate.frame % 2 == 0 and gamestate.menu_state != melee.Menu.UNKNOWN_MENU:
        controller.empty_input()
        return

    if gamestate.menu_state == melee.Menu.MAIN_MENU:
        if gamestate.submenu == melee.SubMenu.MAIN_MENU_SUBMENU:
            if gamestate.menu_selection == 1:
                controller.press_button(melee.Button.BUTTON_A)
            else:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
        elif gamestate.submenu == melee.SubMenu.VS_MODE_SUBMENU:
            if gamestate.menu_selection == 0:
                controller.press_button(melee.Button.BUTTON_A)
            else:
                controller.tilt_analog(melee.Button.BUTTON_MAIN, .5, 0)
        else:
            controller.press_button(melee.Button.BUTTON_B)
    elif gamestate.menu_state == melee.Menu.PRESS_START:
        controller.press_button(melee.Button.BUTTON_START)
    else:
        controller.empty_input()

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

dtm_buffers = {}

with open("Initial_Inputs2.dtm", 'rb') as f:
    buffer_intitial = dtm.read_input(f.read())

with open("pokefloats_segment_1.dtm", 'rb') as f:
    pokedloats_dtm = dtm.read_input(f.read())

with open("segment_1.dtm", 'rb') as f:
    dtm_buffers[0xc0] = dtm.read_input(f.read())

with open("skip_scores.dtm", 'rb') as f:
    buffer_skip_scores = dtm.read_input(f.read())

with open("segment_3.dtm", 'rb') as f:
    dtm_buffers[0xc2] = dtm.read_input(f.read())

with open("segment_5.dtm", 'rb') as f:
    dtm_buffers[0xb6] = dtm.read_input(f.read())

with open("segment_7.dtm", 'rb') as f:
    dtm_buffers[0xb5] = dtm.read_input(f.read())

with open("segment_9.dtm", 'rb') as f:
    dtm_buffers[0xbe] = dtm.read_input(f.read())

with open("segment_11.dtm", 'rb') as f:
    dtm_buffers[0xc9] = dtm.read_input(f.read())

with open("segment_13.dtm", 'rb') as f:
    dtm_buffers[0xc3] = dtm.read_input(f.read())

with open("segment_15.dtm", 'rb') as f:
    dtm_buffers[0xbb] = dtm.read_input(f.read())

with open("segment_17.dtm", 'rb') as f:
    dtm_buffers[0xc4] = dtm.read_input(f.read())

with open("segment_19.dtm", 'rb') as f:
    dtm_buffers[0xc6] = dtm.read_input(f.read())

with open("segment_21.dtm", 'rb') as f:
    dtm_buffers[0xb1] = dtm.read_input(f.read())

with open("segment_23.dtm", 'rb') as f:
    dtm_buffers[0xbd] = dtm.read_input(f.read())

with open("segment_25.dtm", 'rb') as f:
    dtm_buffers[0xc8] = dtm.read_input(f.read())

# Play setup dtm (triggers injection)
agent1.controller.dtm_mode = True
agent1.controller.send_whole_dtm(buffer_intitial)

# Plug our controller in
print("Connecting to TASTM32...")
controller_one.connect()
print("Connected")
numSent = 0

# Main loop
while True:
    # "step" to the next frame
    gamestate = console.step()
    print(gamestate.menu_state, gamestate._menu_scene, gamestate.frame)
    # if 1 in gamestate.players:
    #     print(gamestate.players[1].position.x, gamestate.players[1].position.y)
    if log:
        log.log("Notes", "Processing Time: "  + str(console.processingtime * 1000) + "ms")

    # What menu are we in?
    if gamestate.menu_state == melee.Menu.IN_GAME:

        # Pokefloats
        if gamestate.stage_raw == 0x17:
            if gamestate.frame == -123:
                agent1.controller.reset_tastm32(False)
                agent1.controller.dtm_mode = True
                continue
            if gamestate.frame == -100:
                agent1.controller.pause_dtm()
                numSent = agent1.controller.preload_dtm(pokedloats_dtm)
                continue
            # TODO : desync here
            if gamestate.frame == -90:
                agent1.controller.unpause_dtm()
                agent1.controller.send_remaining_dtm(pokedloats_dtm[numSent:])
                continue

        if gamestate.stage_raw not in [0xC0, 0xC2, 0xb6, 0xb5, 0xbe, 0xc9, 0xc3, 0xbb, 0xc4, 0xc6, 0xb1, 0xbd, 0xc8]:
            print("Waiting area", gamestate.frame, gamestate.stage_raw)
            if gamestate.frame == -123:
                agent1.controller.reset_tastm32(True)
                agent1.controller.dtm_mode = False
            if gamestate.frame == -122:
                agent1.controller.empty_input()
            else:
                agent1.controller.tilt_analog(melee.Button.BUTTON_MAIN, 1, .5)
        else:
            if gamestate.frame == -123:
                print("RNG state:", hex(gamestate.rng_state))
                agent1.controller.reset_tastm32(False)
                agent1.controller.dtm_mode = True
            if gamestate.frame == -100:
                agent1.controller.pause_dtm()
                numSent = agent1.controller.preload_dtm(dtm_buffers[gamestate.stage_raw])
                print("Number of bytes preloaded: ", numSent)
            if gamestate.frame == -40:
                print("Unpausing and sending the remainder")
                agent1.controller.unpause_dtm()
                agent1.controller.send_remaining_dtm(dtm_buffers[gamestate.stage_raw][numSent:])
                print("done sending dtm")
            # There's ONE frame at the end of the game where a player has 0 stocks
            # Are ALL opponents dead?
            game_finished = True
            for player in gamestate.players:
                if player == 1:
                    continue
                if gamestate.players[player].stock > 0:
                    game_finished = False
            if game_finished:
                agent1.controller.send_whole_dtm(buffer_skip_scores)
                print("Done sending whole DTM")

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
        # 261 is the <3 <3 <3 in-between stage
        if gamestate._menu_scene != 261:
            if pokefloats_finished:
                agent1.controller.dtm_mode = False
                naviate_to_allstar(gamestate, agent1.controller)
            else:
                agent1.controller.dtm_mode = False
                navigate_to_pokefloats(gamestate, agent1.controller)
