#include <cmath>

#include "Wavedash.h"

void Wavedash::PressButtons()
{
    //Do nothing if we're in hitlag
    if(m_state->m_memory->player_two_hitlag_frames_left > 0)
    {
        if(m_hitlagFrames == 0)
        {
            m_hitlagFrames = m_state->m_memory->player_two_hitlag_frames_left;
        }
        m_controller->emptyInput();
        return;
    }

    int frame = m_state->m_memory->frame - m_startingFrame;

    //Jump on the first frame possible
    if(frame == 0)
    {
        m_frameJumped = m_state->m_memory->frame;
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    //Let go of jump the very next frame
    if(frame == 1)
    {
        m_controller->emptyInput();
        return;
    }

    //If this is the first knee bend animation, keep track of this frame
    if(m_state->m_memory->player_two_action == KNEE_BEND &&
        m_frameKneeBend == 0)
    {
        m_frameKneeBend = m_state->m_memory->frame;
        return;
    }

    //One frame after knee bend happened, air dodge into the stage
    if(m_state->m_memory->frame == m_frameKneeBend+1)
    {
        m_controller->pressButton(Controller::BUTTON_L);
        //If we're close to the edge, don't wavedash off
        if(std::abs(m_state->m_memory->player_two_x) + 2 > m_state->getStageEdgeGroundPosition())
        {
            //If we're super duper close the the edge, we HAVE to wavedash back, or die
            if(m_state->m_memory->player_two_x > 0)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .2, .2);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .8, .2);
            }
        }
        else if(std::abs(m_state->m_memory->player_two_x) + 10 > m_state->getStageEdgeGroundPosition())
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, .2);
        }
        else
        {
            if(m_isright)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .8, .2);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .2, .2);
            }
        }
        return;
    }

    //Two frames after knee bend, let go of the buttons
    if(m_state->m_memory->frame == m_frameKneeBend+2)
    {
        m_controller->emptyInput();
        return;
    }

    //If somehow we got into the air, then air dodge again (this happens sometimes if the air dodge doesn't work. Not sure why.)
    if(m_state->m_memory->player_two_action == JUMPING_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_BACKWARD)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isright ? .8 : .2, .2);
        return;
    }

    m_controller->emptyInput();
}

bool Wavedash::IsInterruptible()
{
    int frame = m_state->m_memory->frame - m_startingFrame;

    if(frame > 20)
    {
        return true;
    }
    if(m_state->m_memory->player_two_action == LANDING_SPECIAL)
    {
        return true;
    }
    return false;
}

Wavedash::Wavedash(bool isRight)
{
    m_startingFrame = m_state->m_memory->frame;
    m_frameJumped = 0;
    m_hitlagFrames = 0;
    m_frameKneeBend = 0;
    m_isright = isRight;
}

Wavedash::~Wavedash()
{
}
