from util import enums
import csv

class PlayerState:
    character = 2 #TODO enum
    x = 0
    y = 0
    percent = 0
    stock = 0
    facing = True
    action = 2 #TODO enum
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

    #Process one new memory update
    def update(self, mem_update):
        tokens = mem_update[0].split(" ")
        token_count = len(tokens)
        if token_count > 2:
            #Linked list
            pass
        else:
            #Static address or pointer
            print(mem_update[1])
            print(self.locations[mem_update[0]])
