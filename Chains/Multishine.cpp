#include "Multishine.h"
#include "../Util/Logger.h"

Multishine::Multishine()
{
    m_startingFrame = m_state->m_memory->frame;
    Logger::Instance()->Log(INFO, "Start Multishine");
    m_canInterrupt = true;
}

Multishine::~Multishine()
{
}

bool Multishine::IsInterruptible()
{
    //Safety return
    uint frame = m_state->m_memory->frame - m_startingFrame;
    if(frame >= 30)
    {
        return true;
    }

    return m_canInterrupt;
}

void Multishine::PressButtons()
{
    m_canInterrupt = true;

    //If standing, shine
    if(m_state->m_memory->player_two_action == STANDING)
    {
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        m_canInterrupt = false;
        return;
    }

    //Shine on the last frame of knee bend
    if(m_state->m_memory->player_two_action == KNEE_BEND &&
        m_state->m_memory->player_two_action_frame >= 3)
    {
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        m_canInterrupt = false;
        return;
    }

    if(m_state->m_memory->player_two_action == KNEE_BEND)
    {
        m_controller->emptyInput();
        return;
    }

    //Jump on the last frame of shine stun
    if((m_state->m_memory->player_two_action == DOWN_B_STUN ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND_START) &&
        m_state->m_memory->player_two_action_frame >= 4 &&
        m_state->m_memory->player_two_on_ground)
    {
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    if(m_state->m_memory->player_two_action == DOWN_B_GROUND)
    {
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    if(m_state->m_memory->player_two_action == DOWN_B_STUN)
    {
        m_controller->emptyInput();
        return;
    }

    m_controller->emptyInput();
}
