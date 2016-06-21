#include <cmath>

#include "GrabEdge.h"
#include "TransitionHelper.h"

void GrabEdge::PressButtons()
{
    if(m_isInFastfall)
    {
        m_controller->emptyInput();
        return;
    }

    //We can't run if we're in knee bend or shine. We're in a wavedash so let's just accept that
    if(m_state->m_memory->player_two_action == KNEE_BEND ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND)
    {
        m_isInWavedash = true;
    }

    //If we're far away from the edge, then dash at the edge
    if(!m_isInWavedash && (std::abs(m_state->m_memory->player_two_x) < m_state->getStageEdgeGroundPosition() - 13))
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? 0 : 1, .5);
        return;
    }

    m_isInWavedash = true;

    //Fastfall once in the air
    if((m_state->m_memory->player_two_action == FALLING) &&
        !m_isInFastfall)
    {
        if(m_state->m_memory->player_two_speed_y_self < 0)
        {
            m_isInFastfall = true;
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
            return;
        }
        else
        {
            m_controller->emptyInput();
            return;
        }

    }

    double distanceFromEdge = m_state->getStageEdgeGroundPosition() - std::abs(m_state->m_memory->player_two_x);

    //Dash Backwards if we're facing towards the edge and are in a state where we can dash
    // Or if we're too close to safely wavedash back
    if(m_isLeftEdge != m_state->m_memory->player_two_facing ||
        distanceFromEdge < 3)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? 1 : 0, .5);
        return;
    }

    //Once we're dashing away from the edge, jump
    if(m_state->m_memory->player_two_action == DASHING ||
        m_state->m_memory->player_two_action == STANDING ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    //Just hang out and do nothing while initial knee bending
    if(m_state->m_memory->player_two_action == KNEE_BEND &&
        m_state->m_memory->player_two_action_frame < 3)
    {
        m_controller->emptyInput();
        return;
    }

    //Apparently you can be temporarily standing a little past the normal edge of the stage
    double edgeDistance = std::abs(m_state->getStageEdgeGroundPosition() + .5 - std::abs(m_state->m_memory->player_two_x));
    bool slidingTowardEdge = (m_state->m_memory->player_two_speed_ground_x_self > 0) != m_isLeftEdge;

    //If we're about to slide off next frame. Just let it happen, don't air dodge
    if(slidingTowardEdge &&
        std::abs(m_state->m_memory->player_two_speed_ground_x_self) > edgeDistance)
    {
        m_controller->emptyInput();
        return;
    }

    //Once we're in the air, airdodge backwards to the edge
    if((!m_state->m_memory->player_two_on_ground && m_isInWavedash) ||
        (m_state->m_memory->player_two_action == KNEE_BEND &&
        m_state->m_memory->player_two_action_frame >= 3))
    {
        m_controller->pressButton(Controller::BUTTON_L);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? .2 : .8, .2);
        return;
    }

    //Just hang out and do nothing while wave landing
    if(m_state->m_memory->player_two_action == WAVEDASH_SLIDE)
    {
        m_controller->emptyInput();
        return;
    }

    m_controller->emptyInput();
}

bool GrabEdge::IsInterruptible()
{
    bool facingOut = m_state->m_memory->player_two_facing == m_isLeftEdge;

    //If we need to fastfall and haven't yet, don't leave
    if((m_state->m_memory->player_two_action == FALLING) && !m_isInFastfall)
    {
        return false;
    }

    //If we're in this state, something horrible has happened. We won't grab the edge. Abort
    if(facingOut && !m_state->m_memory->player_two_on_ground)
    {
        return true;
    }

    if(!m_isInWavedash)
    {
        return true;
    }
    if(m_state->m_memory->player_two_action == EDGE_HANGING)
    {
        return true;
    }
    //Don't permanently get stuck here
    uint frame = m_state->m_memory->frame - m_startingFrame;
    if(frame > 60)
    {
        return true;
    }
    return false;
}

GrabEdge::GrabEdge()
{
    //Quick variable to tell us which edge to grab
    if(m_state->m_memory->player_one_x > 0)
    {
        m_isLeftEdge = false;
    }
    else
    {
        m_isLeftEdge = true;
    }
    m_startingFrame = m_state->m_memory->frame;
    m_isInWavedash = false;
    m_isInFastfall = false;
}

GrabEdge::~GrabEdge()
{
}
