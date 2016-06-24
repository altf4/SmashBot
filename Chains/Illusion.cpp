#include "Illusion.h"

void Illusion::PressButtons()
{
    if(m_state->m_memory->player_two_action != FOX_ILLUSION &&
        m_state->m_memory->player_two_action != FOX_ILLUSION_START &&
        m_state->m_memory->player_two_action != FOX_ILLUSION_SHORTENED)
    {
        //Jump
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_goRight ? 1 : 0, .5);
        m_controller->pressButton(Controller::BUTTON_B);
        return;
    }

    m_controller->emptyInput();
}

//We're always interruptible during a Walk
bool Illusion::IsInterruptible()
{
    if(m_state->m_memory->player_two_action == FOX_ILLUSION ||
        m_state->m_memory->player_two_action == FOX_ILLUSION_START ||
        m_state->m_memory->player_two_action == FOX_ILLUSION_SHORTENED)
    {
        return false;
    }
    return true;
}

Illusion::Illusion(bool right)
{
    m_goRight = right;
}

Illusion::~Illusion()
{
}
