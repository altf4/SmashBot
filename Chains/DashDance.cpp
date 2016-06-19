#include <cmath>

#include "DashDance.h"
#include "../Util/Constants.h"

void DashDance::PressButtons()
{
    //Avoid moonwalking
    if(m_state->m_moonwalkRisk)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        m_moonwalkPrevent = true;
        return;
    }
    if(m_moonwalkPrevent)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        m_moonwalkPrevent = false;
        return;
    }

    //If we're walking, stop for a frame
    if(m_state->m_memory->player_two_action == WALK_SLOW ||
        m_state->m_memory->player_two_action == WALK_MIDDLE ||
        m_state->m_memory->player_two_action == WALK_FAST)
    {
        m_controller->emptyInput();
        return;
    }

    //If we're starting the turn around animation, keep pressing that way or else we'll get stuck in the slow turnaround
    if(m_state->m_memory->player_two_action == TURNING &&
        m_state->m_memory->player_two_action_frame == 1)
    {
        return;
    }

    //Dash back, since we're about to start running
    if(m_state->m_memory->player_two_action == DASHING &&
        m_state->m_memory->player_two_action_frame >= FOX_DASH_FRAMES-1)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, !m_state->m_memory->player_two_facing, .5);
        return;
    }

    //We can't dash RIGHT after landing. So just chill for a bit
    if((m_state->m_memory->player_two_action == LANDING && m_state->m_memory->player_two_action_frame < 2) ||
        !m_state->m_memory->player_two_on_ground)
    {
        m_controller->emptyInput();
        return;
    }

    //Don't run off the stage
    if(std::abs(m_state->m_memory->player_two_x) > m_state->getStageEdgeGroundPosition() - (3 * FOX_DASH_SPEED))
    {
        bool onLeft = m_state->m_memory->player_two_x < 0;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onLeft ? 1 : 0, .5);
        return;
    }

    //Are we outside the given radius of dash dancing?
    if(m_state->m_memory->player_two_x < m_pivotPoint - m_radius)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, 1, .5);
        return;
    }
    if(m_state->m_memory->player_two_x > m_pivotPoint + m_radius)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, .5);
        return;
    }

    //Keep running the direction we're going
    m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_state->m_memory->player_two_facing ? 1 : 0, .5);
    return;
}

//We're always interruptible during a DashDance
bool DashDance::IsInterruptible()
{
    return true;
}

DashDance::DashDance(double pivot, double radius)
{
    m_pivotPoint = pivot;
    m_radius = radius;
    m_moonwalkPrevent = false;
}

DashDance::~DashDance()
{
}
