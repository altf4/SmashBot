#include <cmath>
#include <cstdlib>
#include <stdlib.h>
#include <algorithm>

#include "MarthKiller.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"

void MarthKiller::PressButtons()
{
    bool onRight = m_state->m_memory->player_one_x > 0;

    double distanceFromEdge = m_state->getStageEdgeGroundPosition() - std::abs(m_state->m_memory->player_two_x);

    //Dash back, since we're about to start running
    if(m_state->m_memory->player_two_action == DASHING &&
        m_state->m_memory->player_two_action_frame >= FOX_DASH_FRAMES-1)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, !m_state->m_memory->player_two_facing, .5);
        return;
    }

    //Should we hard shield right now?
    //Note: Our "facing" bool doesn't change right away in the turning animation. So it looks here like it's backwards.
    // But it's not
    if(m_state->m_memory->player_two_action == TURNING &&
        m_state->m_memory->player_two_facing == onRight &&
        distanceFromEdge < 1.4)
     {
         m_controller->pressButton(Controller::BUTTON_L);
         return;
     }

     //If we're starting the turn around animation, keep pressing that way or else we'll get stuck in the slow turnaround
     if(m_state->m_memory->player_two_action == TURNING &&
         m_state->m_memory->player_two_action_frame == 1)
     {
         //If we're turning back towards the stage, and didn't shield, then we need to do a random backoff
         if(m_state->m_memory->player_two_facing == onRight)
         {
             m_backoffFrames = (rand() % 5) + 1;
         }
         return;
     }

    //Are we in position to pivot?
    if(m_state->m_memory->player_two_action == DASHING &&
        m_state->m_memory->player_two_facing == onRight &&
        distanceFromEdge < FOX_DASH_SPEED + FOX_TURN_SLIDE)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? 0 : 1, .5);
        return;
    }

    //Dash at the edge if we're not close enough
    if(m_state->m_memory->player_two_action == DASHING ||
        m_state->m_memory->player_two_action == TURNING ||
        distanceFromEdge > FOX_DASH_SPEED + FOX_TURN_SLIDE)
    {
        //Unless we're trying to re-roll how far we are from the edge at pivot
        if(m_backoffFrames > 0)
        {
            m_backoffFrames--;
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? 0 : 1, .5);
            return;
        }
        else
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? 1 : 0, .5);
            return;
        }
    }

    //Once we're shielding, let go of the hard shield and start light shielding
    if(m_state->m_memory->player_two_action == SHIELD_START ||
        m_state->m_memory->player_two_action == SHIELD ||
        m_state->m_memory->player_two_action == SHIELD_STUN ||
        m_state->m_memory->player_two_action == SHIELD_REFLECT)
    {
        //Incrementally hold further to the side to avoid rolling
        m_controller->releaseButton(Controller::BUTTON_L);
        m_controller->pressShoulder(Controller::BUTTON_L, .4);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? .5 + m_lightShieldDirection : .5 - m_lightShieldDirection, .5);
        //Increment by .05 each frame, up to the max of .5
        m_lightShieldDirection += .02;
        m_lightShieldDirection = std::min((double)m_lightShieldDirection, .5);
        return;
    }

    //If all else fails, just hang out and do nothing
    m_controller->emptyInput();
}

bool MarthKiller::IsInterruptible()
{
    if(m_state->m_memory->player_one_action == DEAD_FALL ||
        m_state->m_memory->player_one_action == DEAD_DOWN ||
        m_state->m_memory->player_one_on_ground)
    {
        return true;
    }

    if(m_state->m_memory->player_one_action == UP_B &&
        m_state->m_memory->player_two_action != SHIELD_REFLECT &&
        m_state->m_memory->player_two_action != SHIELD &&
        m_state->m_memory->player_two_action != SHIELD_START)
    {
        return true;
    }

    //Get unstuck eventually. Shouldn't get here.
    uint frame = m_state->m_memory->frame - m_startingFrame;
    if(frame > 240)
    {
        m_controller->emptyInput();
        return true;
    }

    return false;
}

MarthKiller::MarthKiller()
{
    m_backoffFrames = 0;
    m_lightShieldDirection = 0;
}

MarthKiller::~MarthKiller()
{
}
