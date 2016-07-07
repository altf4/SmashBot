#include <cmath>
#include <cstdlib>

#include "../Util/Constants.h"
#include "Waveshine.h"

void Waveshine::PressButtons()
{
    //If we're falling off the stage, then we must have slid off. Jump back on.
    //(Also, make sure that we're not trying to jump two frames in a row. If so, it would be interpreted as one jump)
    if(m_state->m_memory->player_two_action == FALLING &&
        std::abs(m_state->m_memory->player_two_x) > m_state->getStageEdgeGroundPosition() &&
        m_state->m_memory->frame != m_frameJumped+1)
    {
        bool onRight = m_state->m_memory->player_two_x > 0;
        m_frameJumped = m_state->m_memory->frame;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? 0 : 1, .5);
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    //If they're hurt and we're chasing them. Then don't try to pivot. Go into a running state then shine
    if(m_frameShined == 0 &&
        m_state->m_memory->player_two_action == DASHING &&
        m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_hitstun_frames_left > (FOX_DASH_FRAMES - m_state->m_memory->player_two_action_frame))
    {
        bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, onRight ? 0 : 1, .5);
        return;
    }

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

    //Pivot shine! You can't shine from a dash animation. So make it a pivot
    if(m_frameShined == 0 &&
        m_state->m_memory->player_two_action == DASHING)
    {
        bool facingRight = m_state->m_memory->player_two_facing;
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, facingRight ? 0 : 1, .5);
        return;
    }

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

    if(m_frameShined == 0)
    {
        //Shine
        m_isBusy = true;
        m_frameShined = m_state->m_memory->frame;
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        return;
    }

    if(m_state->m_memory->frame == m_frameShined+m_hitlagFrames+1)
    {
        //Let go of down b
        m_controller->releaseButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        return;
    }

    if(m_state->m_memory->frame == m_frameShined+m_hitlagFrames+4)
    {
        //Jump out of our shine
        m_frameJumped = m_state->m_memory->frame;
        m_controller->pressButton(Controller::BUTTON_Y);
        return;
    }

    if(m_state->m_memory->frame == m_frameJumped+1)
    {
        m_controller->releaseButton(Controller::BUTTON_Y);
        return;
    }

    if(m_state->m_memory->player_two_action == KNEE_BEND &&
        m_frameKneeBend == 0)
    {
        m_frameKneeBend = m_state->m_memory->frame;
        return;
    }

    //If we're in the air, there won't be any knee bending frames
    if(m_state->m_memory->frame == m_frameKneeBend+1 ||
        m_state->m_memory->player_two_action == JUMPING_ARIAL_FORWARD ||
        m_state->m_memory->player_two_action == JUMPING_ARIAL_BACKWARD)
    {
        m_airdodgeFrame = m_state->m_memory->frame;
        m_controller->pressButton(Controller::BUTTON_L);
        //TODO: still assumes we're facing the opponent
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
        //If we're only kinda close to the edge, just wavedash downward
        else if(std::abs(m_state->m_memory->player_two_x) + 18 > m_state->getStageEdgeGroundPosition())
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        }
        else
        {
            if(m_state->m_memory->player_one_x > m_state->m_memory->player_two_x)
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

    if(m_state->m_memory->frame == m_airdodgeFrame+1)
    {
        m_isBusy = false;
        m_controller->releaseButton(Controller::BUTTON_L);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
        return;
    }
}

bool Waveshine::IsInterruptible()
{
    //If the enemy is off the stage, let's quit early
    if(std::abs(m_state->m_memory->player_one_x) > m_state->getStageEdgeGroundPosition() + .001)
    {
        return true;
    }

    if(m_state->m_memory->frame - m_startingFrame > 20)
    {
        return true;
    }
    return !m_isBusy;
}

Waveshine::Waveshine()
{
    m_startingFrame = m_state->m_memory->frame;
    m_frameJumped = 0;
    m_frameShined = 0;
    m_hitlagFrames = 0;
    m_frameKneeBend = 0;
    m_airdodgeFrame = 0;
    m_isBusy = false;
    m_moonwalkPrevent = false;
}

Waveshine::~Waveshine()
{
}
