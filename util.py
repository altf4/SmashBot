import melee

"""Modlate a number from 0-action_dim into discrete button presses"""
#TODO: Verify this better
def action_to_presses(action):
    button_int = action % 6
    button = None
    if button_int == 0:
        button = melee.enums.Button.BUTTON_A
    if button_int == 1:
        button = melee.enums.Button.BUTTON_B
    if button_int == 2:
        button = melee.enums.Button.BUTTON_L
    if button_int == 3:
        button = melee.enums.Button.BUTTON_Y
    if button_int == 4:
        button = melee.enums.Button.BUTTON_Z
    if button_int == 5:
        button = None

    x_int = (action // 6) % 7
    x = 0.5
    if x_int == 0:
        x = 0
    if x_int == 1:
        x = 0.2
    if x_int == 2:
        x = 0.4
    if x_int == 3:
        x = 0.5
    if x_int == 4:
        x = 0.6
    if x_int == 5:
        x = 0.8
    if x_int == 6:
        x = 1

    y_int = (action // (6*7)) % 7
    y = 0.5
    if y_int == 0:
        y = 0
    if y_int == 1:
        y = 0.2
    if y_int == 2:
        y = 0.4
    if y_int == 3:
        y = 0.5
    if y_int == 4:
        y = 0.6
    if y_int == 5:
        y = 0.8
    if y_int == 6:
        y = 1

    return x, y, button

"""Turn a ControllerState object into a list that we want for Keras"""
def action_toint(action):
    #The recording COULD press more than one button. So if they do, let's just pretend
    # like only one happened and hope it's rare enough to not matter much
    button_int = 5
    if action.button[melee.enums.Button.BUTTON_A]:
        button_int = 0
    if action.button[melee.enums.Button.BUTTON_B]:
        button_int = 1
    if action.button[melee.enums.Button.BUTTON_L]:
        button_int = 2
    if action.button[melee.enums.Button.BUTTON_Y]:
        button_int = 3
    if action.button[melee.enums.Button.BUTTON_Z]:
        button_int = 4

    #Round to the nearest analog stick value
    x, y = action.main_stick

    x_int = 3
    #0.9 -> 1.0
    if x > 0.9:
        x_int = 6
    #0.7 -> 0.9
    elif x > 0.7:
        x_int = 5
    #0.55 -> 0.7
    elif x > 0.55:
        x_int = 4
    #0.45 -> 0.55
    elif x > 0.45:
        x_int = 3
    #0.3 -> 0.45
    elif x > 0.3:
        x_int = 2
    #0.1 -> 0.3
    elif x > 0.1:
        x_int = 1
    #0.0 -> 0.1
    elif x < 0.1:
        x_int = 0

    y_int = 3
    #0.9 -> 1.0
    if y > 0.9:
        y_int = 6
    #0.7 -> 0.9
    elif y > 0.7:
        y_int = 5
    #0.55 -> 0.7
    elif y > 0.55:
        y_int = 4
    #0.45 -> 0.55
    elif y > 0.45:
        y_int = 3
    #0.3 -> 0.45
    elif y > 0.3:
        y_int = 2
    #0.1 -> 0.3
    elif y > 0.1:
        y_int = 1
    #0.0 -> 0.1
    elif y < 0.1:
        y_int = 0

    return button_int + (x_int * 6) + (y_int * 6*7)

def buttons_to_state(x,y,button_new):
    state = melee.controller.ControllerState()
    state.main_stick = (x,y)
    state.button[button_new] = True
    return state
