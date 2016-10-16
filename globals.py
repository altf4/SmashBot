from util import gamestate, controller, logger

#Create these objects here and then never again
def init(smashbot_port, opponent_port):
    global gamestate
    gamestate = gamestate.GameState()
    global controller
    controller = controller.Controller(smashbot_port)
    global smashbot_state
    smashbot_state = gamestate.player[smashbot_port]
    global opponent_state
    opponent_state = gamestate.player[opponent_port]
    global log
    log = logger.Logger()
