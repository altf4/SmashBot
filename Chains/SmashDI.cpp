#include "SmashDI.h"

SmashDI::SmashDI(bool goRight)
{
    m_goRight = goRight;
    m_alternateDirection = true;
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

    //Safety return. In case we screw something up, don't permanently get stuck in this chain.
    if(m_state->m_memory->frame - m_startingFrame > 60)
    {
        return true;
    }
    return false;
}

void SmashDI::PressButtons()
{
    //Alternate each frame between UP and LEFT/RIGHT so we can SDI every frame of hitlag
    m_alternateDirection = !m_alternateDirection;

    double tilt = 0.5;
    if(m_goRight)
    {
        tilt += 0.5;
    }

    //Go right if facing right, otherwise go left
    m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_alternateDirection ? tilt - 0.5 : tilt, m_alternateDirection ? 0.5 : 1);
}
