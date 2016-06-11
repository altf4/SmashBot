#include "HoldShield.h"

void HoldShield::PressButtons()
{
    if(m_state->m_memory->frame - m_startingFrame == 0 &&
        m_state->m_memory->player_two_action == DASHING)
    {
        m_controller->emptyInput();
        return;
    }
    else
    {
        m_holdFrames--;
        m_controller->pressButton(Controller::BUTTON_L);
        return;
    }
}

bool HoldShield::IsInterruptible()
{
    if(m_holdFrames > 0)
    {
        return false;
    }
    else
    {
        return true;
    }
}

HoldShield::HoldShield(int frames)
{
    m_startingFrame = m_state->m_memory->frame;
    m_holdFrames = frames;
}

HoldShield::~HoldShield()
{
    m_controller->releaseButton(Controller::BUTTON_L);
}
