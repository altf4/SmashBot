#include "JumpCanceledShine.h"

JumpCanceledShine::JumpCanceledShine()
{
    m_startingFrame = m_state->m_memory->frame;
}

JumpCanceledShine::~JumpCanceledShine()
{
}

bool JumpCanceledShine::IsInterruptible()
{
    if(m_state->m_memory->player_two_action == JUMPING_ARIAL_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_ARIAL_BACKWARD ||
        m_state->m_memory->player_two_action == JUMPING_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_BACKWARD)
    {
        return true;
    }

    uint frame = m_state->m_memory->frame - m_startingFrame;
    if(frame >= 20)
    {
        return true;
    }
    return false;
}

void JumpCanceledShine::PressButtons()
{
    //If we're on the edge, drop down
    if(m_state->m_memory->player_two_action == EDGE_HANGING)
    {
        bool onRight = m_state->m_memory->player_two_x > 0;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? .8 : .2, .5);
        return;
    }

    //Jump out of our shine
    if(m_state->m_memory->player_two_action == DOWN_B_AIR ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND)
    {
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    //Let go of jump if we're jumping
    if(m_state->m_memory->player_two_action == JUMPING_ARIAL_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_ARIAL_BACKWARD ||
        m_state->m_memory->player_two_action == JUMPING_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_BACKWARD)
    {
        m_controller->emptyInput();
        return;
    }

    //Shine
    if(m_state->m_memory->player_two_action != DOWN_B_STUN &&
        m_state->m_memory->player_two_action != DOWN_B_AIR)
    {
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        return;
    }
    else
    {
        m_controller->emptyInput();
        return;
    }
}
