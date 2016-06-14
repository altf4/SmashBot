#include "Illusion.h"

void Illusion::PressButtons()
{
    if(!m_pressedSideB)
    {
        m_pressedSideB = true;
        //Jump
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_goRight ? 1 : 0, .5);
        m_controller->pressButton(Controller::BUTTON_B);
    }
    else
    {
        m_controller->emptyInput();
        m_pressedSideB = false;
    }
}

//We're always interruptible during a Walk
bool Illusion::IsInterruptible()
{
    return true;
}

Illusion::Illusion(bool right)
{
    m_pressedSideB = false;
    m_goRight = right;
}

Illusion::~Illusion()
{
}
