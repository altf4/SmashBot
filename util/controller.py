from util import paths, enums, logger
import copy
import globals

class ControllerState:
    def __init__(self):
        self.button = dict()
        #Boolean buttons
        self.button[enums.Button.BUTTON_A] = False
        self.button[enums.Button.BUTTON_B] = False
        self.button[enums.Button.BUTTON_X] = False
        self.button[enums.Button.BUTTON_Y] = False
        self.button[enums.Button.BUTTON_Z] = False
        self.button[enums.Button.BUTTON_L] = False
        self.button[enums.Button.BUTTON_R] = False
        self.button[enums.Button.BUTTON_START] = False
        self.button[enums.Button.BUTTON_D_UP] = False
        self.button[enums.Button.BUTTON_D_DOWN] = False
        self.button[enums.Button.BUTTON_D_LEFT] = False
        self.button[enums.Button.BUTTON_D_RIGHT] = False
        #Analog sticks
        self.main_stick = (.5, .5)
        self.c_stick = (.5, .5)
        #Analog shoulders
        self.l_shoulder = 0
        self.r_shoulder = 0

class Controller:
    def __init__(self, port):
        pipe_path = paths.get_dolphin_pipes_path(port)
        self.pipe = open(pipe_path, "w")
        self.prev = ControllerState()
        self.current = ControllerState()

    def press_button(self, button):
        command = "PRESS " + str(button.value) + "\n"
        log = globals.log
        log.log("Buttons Pressed", command, concat=True)
        self.current.button[button] = True
        self.pipe.write(command)

    def release_button(self, button):
        command = "RELEASE " + str(button.value) + "\n"
        log = globals.log
        log.log("Buttons Pressed", command, concat=True)
        self.current.button[button] = False
        self.pipe.write(command)

    def press_shoulder(self, button, amount):
        command = "SET " + str(button.value) + " " + str(amount) + "\n"
        log = globals.log
        log.log("Buttons Pressed", command, concat=True)
        if button == enums.Button.BUTTON_L:
            self.current.l_shoulder = amount
        elif button == enums.Button.BUTTON_R:
            self.current.r_shoulder = amount
        self.pipe.write(command)

    def tilt_analog(self, button, x, y):
        command = "SET " + str(button.value) + " " + str(x) + " " + str(y) + "\n"
        log = globals.log
        log.log("Buttons Pressed", command, concat=True)
        self.pipe.write(command)

    def empty_input(self):
        command = "RELEASE A" + "\n"
        command += "RELEASE B" + "\n"
        command += "RELEASE X" + "\n"
        command += "RELEASE Y" + "\n"
        command += "RELEASE Z" + "\n"
        command += "RELEASE L" + "\n"
        command += "RELEASE R" + "\n"
        command += "RELEASE START" + "\n"
        command += "RELEASE D_UP" + "\n"
        command += "RELEASE D_DOWN" + "\n"
        command += "RELEASE D_LEFT" + "\n"
        command += "RELEASE D_RIGHT" + "\n"
        command += "SET MAIN .5 .5" + "\n"
        command += "SET C .5 .5" + "\n"
        command += "SET L 0" + "\n"
        command += "SET R 0" + "\n"
        self.pipe.write(command)
        log = globals.log
        log.log("Buttons Pressed", "Empty Input", concat=True)

    def flush(self):
        self.pipe.flush()
        #Move the current controller state into the previous one
        self.prev = copy.copy(self.current)
