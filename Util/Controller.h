#ifndef _Controller
#define _Controller

#pragma once

#include <string>

struct ControllerState
{
    //This is missing the D-pad for now. But we probabably won't ever use it anyway
    bool m_a;
    bool m_b;
    bool m_x;
    bool m_y;
    bool m_z;
    bool m_start;
    bool m_l_trigger;
    bool m_r_trigger;

    double m_main_stick_x;
    double m_main_stick_y;

    double m_c_stick_x;
    double m_c_stick_y;

    double m_l_shoulder;
    double m_r_shoulder;
};

class Controller {
public:
    enum BUTTON {
        BUTTON_A,
        BUTTON_B,
        BUTTON_X,
        BUTTON_Y,
        BUTTON_Z,
        BUTTON_L,
        BUTTON_R,
        BUTTON_START,
        BUTTON_D_UP,
        BUTTON_D_DOWN,
        BUTTON_D_LEFT,
        BUTTON_D_RIGHT,
        BUTTON_MAIN,
        BUTTON_C
    };

    static Controller *Instance();
    ControllerState m_prevFrameState;

    void pressButton(BUTTON b);
    void releaseButton(BUTTON b);
    // Analog values are clamped to [0, 1].
    void pressShoulder(BUTTON b, double amount);
    void tiltAnalog(BUTTON B, double x, double y);

    //Press no buttons, move sticks back to neutral
    void emptyInput();

    //Actually writes to the pipe
    void flush();

private:
    Controller();

    std::string m_buffer;
    static Controller *m_instance;
    int m_fifo;
    //Hardcoded strings to send to dolphin
    std::string STRING_A = "A";
    std::string STRING_B = "B";
    std::string STRING_X = "X";
    std::string STRING_Y = "Y";
    std::string STRING_Z = "Z";
    std::string STRING_START = "START";
    std::string STRING_L = "L";
    std::string STRING_R = "R";
    std::string STRING_D_UP = "D_UP";
    std::string STRING_D_DOWN = "D_DOWN";
    std::string STRING_D_LEFT = "D_LEFT";
    std::string STRING_D_RIGHT = "D_RIGHT";
    std::string STRING_C = "C";
    std::string STRING_MAIN = "MAIN";
};

#endif
