from util import paths, enums

class Controller:
    def __init__(self):
        pipe_path = paths.get_dolphin_pipes_path()
        self.pipe = open(pipe_path, "w")

    def press_button(self, button):
        command = "PRESS " + str(button.value) + "\n"
        self.pipe.write(command)

    def release_button(self, button):
        command = "RELEASE " + str(button.value) + "\n"
        self.pipe.write(command)

    def press_shoulder(self, button, amount):
        command = "SET " + str(button.value) + " " + str(amount) + "\n"
        self.pipe.write(command)

    def tilt_analog(self, button, x, y):
        command = "SET " + str(button.value) + " " + str(x) + " " + str(y) + "\n"
        self.pipe.write(command)

    def emptyInput(self):
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
        command += "SET MAIN 0 0" + "\n"
        command += "SET C 0 0" + "\n"
        command += "SET L 0" + "\n"
        command += "SET R 0" + "\n"
        self.pipe.write(command)

    def flush(self):
        self.pipe.flush()
