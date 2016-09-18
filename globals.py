from util import gamestate, controller

#Create these objects here and then never again
def init(smashbot_port, opponent_port):
    global gamestate
    gamestate = gamestate.GameState()
    global controller
    controller = controller.Controller()
    global smashbot_state
    smashbot_state = gamestate.player[smashbot_port]
    global opponent_state
    opponent_state = gamestate.player[opponent_port]
