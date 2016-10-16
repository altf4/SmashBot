from util import enums
import csv
from struct import *

class PlayerState:
    character = enums.Character.UNKNOWN_CHARACTER
    x = 0
    y = 0
    percent = 0
    stock = 0
    facing = True
    action = enums.Action.UNKNOWN_ANIMATION
    action_counter = 0
    action_frame = 0
    invulnerable = False
    hitlag_frames_left = 0
    hitstun_frames_left = 0
    charging_smash = 0
    jumps_left = 0
    on_ground = True
    speed_air_x_self = 0
    speed_y_self = 0
    speed_x_attack = 0
    speed_y_attack = 0
    speed_ground_x_self = 0
    cursor_x = 0
    cursor_y = 0

class GameState:
    frame = 0
    stage = enums.Stage.FINAL_DESTINATION
    menu_state = enums.Menu.CHARACTER_SELECT
    player = dict()

    def __init__(self):
        #Dict with key of address, and value of (name, player)
        self.locations = dict()
        with open("csv/locations.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for line in reader:
                self.locations[line["Address"]] = (line["Name"], line["Player"])
        self.player[1] = PlayerState()
        self.player[2] = PlayerState()
        self.player[3] = PlayerState()
        self.player[4] = PlayerState()

    #Process one new memory update
    def update(self, mem_update):
        tokens = mem_update[0].split(" ")
        token_count = len(tokens)
        #Linked list
        if token_count > 2:
            pass
        #Static address or pointer
        else:
            #Handle one of the globals first
            label = self.locations[mem_update[0]][0]
            player_int = int(self.locations[mem_update[0]][1])
            if label == "frame":
                self.frame = unpack('>I', mem_update[1])[0]
                return True
            if label == "stage":
                self.stage = unpack('>I', mem_update[1])[0]
                self.stage = self.stage >> 16
                try:
                    self.stage = enums.Stage(self.stage)
                except ValueError:
                    self.stage = enums.Stage.NO_STAGE
                return False
            if label == "menu_state":
                self.menu_state = unpack('>I', mem_update[1])[0]
                self.menu_state &= 0x000000ff
                self.menu_state = enums.Menu(self.menu_state)
                return False
            #Player variables
            if label == "percent":
                self.player[player_int].percent = unpack('>I', mem_update[1])[0]
                self.player[player_int].percent = self.player[player_int].percent >> 16
                return False
            if label == "stock":
                self.player[player_int].stock = unpack('>I', mem_update[1])[0]
                self.player[player_int].stock = self.player[player_int].stock >> 24
                return False
            if label == "facing":
                self.player[player_int].facing = unpack('>I', mem_update[1])[0]
                self.player[player_int].facing = self.player[player_int].facing >> 31
                return False
            if label == "x":
                self.player[player_int].x = unpack('>f', mem_update[1])[0]
                return False
            if label == "y":
                self.player[player_int].y = unpack('>f', mem_update[1])[0]
                return False
            if label == "character":
                temp = unpack('>I', mem_update[1])[0] >> 24
                try:
                    self.player[player_int].character = enums.Character(temp)
                except ValueError:
                    self.player[player_int].character = enums.Character.UNKNOWN_CHARACTER
                return False
            if label == "cursor_x":
                self.player[player_int].cursor_x = unpack('>f', mem_update[1])[0]
                return False
            if label == "cursor_y":
                self.player[player_int].cursor_y = unpack('>f', mem_update[1])[0]
                return False
            if label == "action":
                temp = unpack('>I', mem_update[1])[0]
                try:
                    self.player[player_int].action = enums.Action(temp)
                except ValueError:
                    self.player[player_int].action = enums.Action.UNKNOWN_ANIMATION
                return False
            if label == "action_counter":
                temp = unpack('I', mem_update[1])[0]
                temp = temp >> 8
                self.player[player_int].action_counter = temp
                return False
            if label == "action_frame":
                temp = unpack('>f', mem_update[1])[0]
                self.player[player_int].action_frame = int(temp)
                return False
            if label == "invulnerable":
                self.player[player_int].invulnerable = unpack('>I', mem_update[1])[0]
                self.player[player_int].invulnerable = self.player[player_int].invulnerable >> 31
                return False
            if label == "hitlag_frames_left":
                temp = unpack('>f', mem_update[1])[0]
                self.player[player_int].hitlag_frames_left = int(temp)
            if label == "hitstun_frames_left":
                temp = unpack('>f', mem_update[1])[0]
                self.player[player_int].hitstun_frames_left = int(temp)
            if label == "charging_smash":
                temp = unpack('>I', mem_update[1])[0]
                if temp == 2:
                    self.player[player_int].charging_smash = True
                else:
                    self.player[player_int].charging_smash = False
                return False
            if label == "jumps_left":
                temp = unpack('>I', mem_update[1])[0]
                temp = temp >> 24
                self.player[player_int].jumps_left = temp
                return False
            if label == "on_ground":
                temp = unpack('>I', mem_update[1])[0]
                if temp == 0:
                    self.player[player_int].on_ground = True
                else:
                    self.player[player_int].on_ground = False
                return False
            if label == "speed_air_x_self":
                self.player[player_int].speed_air_x_self = unpack('>f', mem_update[1])[0]
                return False
            if label == "speed_y_self":
                self.player[player_int].speed_y_self = unpack('>f', mem_update[1])[0]
                return False
            if label == "speed_x_attack":
                self.player[player_int].speed_x_attack = unpack('>f', mem_update[1])[0]
                return False
            if label == "speed_y_attack":
                self.player[player_int].speed_y_attack = unpack('>f', mem_update[1])[0]
                return False
            if label == "speed_ground_x_self":
                self.player[player_int].speed_ground_x_self = unpack('>f', mem_update[1])[0]
                return False
            return False
