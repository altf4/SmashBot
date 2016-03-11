#include "SmashDI.h"

SmashDI::SmashDI(bool facingRight)
{
    m_startingFrame = m_state->m_memory->frame;
    m_facingRight = facingRight;
}

SmashDI::~SmashDI()
{
}

bool SmashDI::IsInterruptible()
{
    //once hitlag is over, the bot is free to do what it wishes
    if(m_state->m_memory->player_two_hitlag_frames_left == 0) 
    {
        return true;
    }
    return false;
}

void SmashDI::PressButtons()
{
    //hitlag_frames_left - 1 is done in order to establish DI correctly
    for(uint i = 0; i <= m_state->m_memory->player_two_hitlag_frames_left; i++)
    {
        //Alternate each frame between UP and LEFT/RIGHT so we can SDI every frame of hitlag
        //Go right if facing right, otherwise go left
        if(i % 2 == 0)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_facingRight ? 1 : 0, 0.5);
            return;
        }
        else {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_facingRight ? 1: 0, 1);
            return;
        }
    }
}
