#include <iostream>

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
    uint frame = m_state->m_memory->frame - m_startingFrame;
    //hitlag_frames_left - 1 is done in order to establish DI correctly
    for(uint i = 0; i <= m_state->m_memory->player_two_hitlag_frames_left; i++)
    {
        //Alternate each frame between UP and LEFT/RIGHT so we can SDI every frame of hitlag
        if(i % 2 == 0)
        {
            //Go right if facing right, otherwise go left
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_facingRight ? 1 : 0, 0.5);
            std::cout << "Debug: SDI'd to the RIGHT on frame " << frame+1 << std::endl;
        }
        else
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_facingRight ? 1 : 0, 1);
            std::cout << "Debug: SDI'd to the RIGHT on frame " << frame+1 << std::endl;
        }
    }
}
