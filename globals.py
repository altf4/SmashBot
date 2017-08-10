import melee

#Create these objects here and then never again
def init(dolphin, smashbot_port, opponent_port):
    global gamestate
    gamestate = melee.gamestate.GameState(dolphin)
    global controller
    controller = melee.controller.Controller(port=smashbot_port, dolphin=dolphin)
    global smashbot_state
    smashbot_state = gamestate.player[smashbot_port]
    global opponent_state
    opponent_state = gamestate.player[opponent_port]
    global framedata
    framedata = melee.framedata.FrameData()
    global logger
    logger = dolphin.logger
    global difficulty
    difficulty = 4
