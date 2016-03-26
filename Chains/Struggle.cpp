#include "Struggle.h"

Struggle::Struggle(bool wiggle)
{
    m_isWiggle = wiggle;
}

Struggle::~Struggle()
{
}

bool Struggle::IsInterruptible()
{
    if(m_isWiggle)
    {
        if(m_state->m_memory->player_two_action == TUMBLING)
        {
            return false;
        }
        else
        {
            return true;
        }
    }

    //Quit if we get out of the grab
    if(m_state->m_memory->player_two_action != GRABBED &&
        m_state->m_memory->player_two_action != GRAB_PULL &&
        m_state->m_memory->player_two_action != GRAB_PUMMELED)
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

void Struggle::PressButtons()
{
    if(m_isWiggle)
    {
        if(m_state->m_memory->frame % 2)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, .5);
        }
        else
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 1, .5);
        }
        return;
    }

    if(m_state->m_memory->player_two_action != GRABBED &&
        m_state->m_memory->player_two_action != GRAB_PULL &&
        m_state->m_memory->player_two_action != GRAB_PUMMELED)
    {
        m_controller->emptyInput();
        return;
    }

    if(m_state->m_memory->frame % 2)
    {
        m_controller->pressButton(Controller::BUTTON_A);
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->pressButton(Controller::BUTTON_X);
        m_controller->pressButton(Controller::BUTTON_Y);
        m_controller->pressButton(Controller::BUTTON_L);
        m_controller->pressButton(Controller::BUTTON_Z);
    }
    else
    {
        m_controller->releaseButton(Controller::BUTTON_A);
        m_controller->releaseButton(Controller::BUTTON_B);
        m_controller->releaseButton(Controller::BUTTON_X);
        m_controller->releaseButton(Controller::BUTTON_Y);
        m_controller->releaseButton(Controller::BUTTON_L);
        m_controller->releaseButton(Controller::BUTTON_Z);
    }

    switch(m_state->m_memory->frame % 4)
    {
        case 0:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
            m_controller->tiltAnalog(Controller::BUTTON_C, .5, 0);
            break;
        }
        case 1:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 1, .5);
            m_controller->tiltAnalog(Controller::BUTTON_C, 1, .5);
            break;
        }
        case 2:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 1);
            m_controller->tiltAnalog(Controller::BUTTON_C, .5, 1);
            break;
        }
        case 3:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, .5);
            m_controller->tiltAnalog(Controller::BUTTON_C, 0, .5);
            break;
        }
    }
}
