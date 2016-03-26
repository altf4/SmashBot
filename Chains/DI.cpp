#include "DI.h"

DI::DI(double x, double y)
{
    m_x = x;
    m_y = y;
}

DI::~DI()
{
}

bool DI::IsInterruptible()
{
    if(!m_state->isDamageState((ACTION)m_state->m_memory->player_two_action))
    {
        return true;
    }

    //Safety return. In case we screw something up, don't permanently get stuck in this chain.
    if(m_state->m_memory->frame - m_startingFrame > 360)
    {
        return true;
    }
    return false;
}

void DI::PressButtons()
{
    m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_x, m_y);
}
