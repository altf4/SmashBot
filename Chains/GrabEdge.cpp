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

    //If we're far away from the edge, then dash at the edge
    if(!m_isInWavedash && (std::abs(m_state->m_memory->player_two_x) < 72.5656))
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? 0 : 1, .5);
        return;
    }

    m_isInWavedash = true;

    //Fastfall once in the air
    if((m_state->m_memory->player_two_action == FALLING) && !m_isInFastfall)
    {
        m_isInFastfall = true;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        return;
    }

    //Dash Backwards if we're facing towards the edge and are in a state where we can dash
    if(m_isLeftEdge != m_state->m_memory->player_two_facing)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? 1 : 0, .5);
        return;
    }

    //Once we're dashing away from the edge, jump
    if(m_state->m_memory->player_two_action == DASHING)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    //Just hang out and do nothing while knee bending
    if(m_state->m_memory->player_two_action == KNEE_BEND)
    {
        m_controller->emptyInput();
        return;
    }

    //Once we're in the air, airdodge backwards to the edge
    if(!m_state->m_memory->player_two_on_ground && m_isInWavedash)
    {
        m_controller->pressButton(Controller::BUTTON_L);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isLeftEdge ? .2 : .8, .2);
        return;
    }

    //Just hang out and do nothing while wave landing
    if(m_state->m_memory->player_two_action == LANDING_SPECIAL)
    {
        m_controller->emptyInput();
        return;
    }

    m_controller->emptyInput();
}

bool GrabEdge::IsInterruptible()
{
    bool facingOut = m_state->m_memory->player_two_facing == m_isLeftEdge;

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
