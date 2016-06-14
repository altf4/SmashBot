#include "FullJump.h"

void FullJump::PressButtons()
{
    if(!m_pressedJump)
    {
        m_pressedJump = true;
        //Jump
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        m_controller->pressButton(Controller::BUTTON_Y);
    }
    else
    {
        m_controller->emptyInput();
        m_pressedJump = false;
    }
}

//We're always interruptible during a Walk
bool FullJump::IsInterruptible()
{
    return true;
}

FullJump::FullJump()
{
    m_pressedJump = false;
}

FullJump::~FullJump()
{
}
