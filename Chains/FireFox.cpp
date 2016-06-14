#include "FireFox.h"
#include "TransitionHelper.h"

void FireFox::PressButtons()
{
    //Firefox
    if(m_state->m_memory->player_two_action != FIREFOX_WAIT_AIR &&
      m_state->m_memory->player_two_action != FIREFOX_AIR)
    {
        if(!m_hasUpBd)
        {
            m_hasUpBd = true;
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 1);
            m_controller->pressButton(Controller::BUTTON_B);
            return;
        }
        else
        {
            m_hasUpBd = false;
            m_controller->emptyInput();
            return;
        }

    }

    if(m_state->m_memory->player_two_action == FIREFOX_WAIT_AIR)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRightEdge ? 0 : 1, 1);
        return;
    }

    if(m_state->m_memory->player_two_action == FIREFOX_AIR)
    {
        m_controller->emptyInput();
        return;
    }
}

bool FireFox::IsInterruptible()
{
    if(m_state->m_memory->player_two_action != FIREFOX_WAIT_AIR &&
      m_state->m_memory->player_two_action != FIREFOX_AIR)
    {
        return true;
    }
    if(m_state->m_memory->frame - m_startingFrame > 100)
    {
        //Safety return. In case we screw something up, don't permanently get stuck in this chain.
        return true;
    }
    return false;
}

FireFox::FireFox()
{
    //Quick variable to tell us which edge we're on
    m_isRightEdge = m_state->m_memory->player_two_x > 0;
    m_startingFrame = m_state->m_memory->frame;
    m_hasUpBd = false;
}

FireFox::~FireFox()
{
}
