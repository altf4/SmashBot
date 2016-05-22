#include <cmath>

#include "Run.h"
void Run::PressButtons()
{
    //If we're starting the turn around animation, keep pressing that way or else we'll get stuck in the slow turnaround
    if(m_state->m_memory->player_two_action == TURNING &&
        m_state->m_memory->player_two_action_frame == 1)
    {
        return;
    }

    //We can't dash RIGHT after landing. So just chill for a bit
    if((m_state->m_memory->player_two_action == LANDING && m_state->m_memory->player_two_action_frame < 2) ||
        !m_state->m_memory->player_two_on_ground)
    {
        m_controller->emptyInput();
        return;
    }

    switch(m_state->m_memory->player_two_action)
    {
        case WALK_SLOW:
        case DASHING:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRight ? 1 : 0, .5);
            break;
        }
        case WALK_MIDDLE:
        case WALK_FAST:
        {
            //Turning around is fine. We'll dash. But we can't run forward. We need to wavedash
            if(m_state->m_memory->player_two_facing != m_isRight)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRight ? 1 : 0, .5);
                break;
            }
            else
            {
                m_wavedashFrameStart = m_state->m_memory->frame;
                m_isWavedashing = true;
                break;
            }
            break;
        }
        case RUNNING:
        {
            //Are we running the wrong way? If so, wavedash back to stop the run
            if(m_state->m_memory->player_two_facing != m_isRight)
            {
                m_wavedashFrameStart = m_state->m_memory->frame;
                m_isWavedashing = true;
                break;
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRight ? 1 : 0, .5);
            }
            break;
        }
        default:
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRight ? 1 : 0, .5);
            break;
        }
    }

}

//We're always interruptible during a Walk
bool Run::IsInterruptible()
{
    return true;
}

Run::Run(bool isRight)
{
    m_isRight = isRight;
}

Run::~Run()
{
}
