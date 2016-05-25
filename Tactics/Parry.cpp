#include <cmath>
#include <typeinfo>

#include "Parry.h"
#include "../Util/Constants.h"
#include "../Chains/Powershield.h"
#include "../Chains/SpotDodge.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/Run.h"
#include "../Chains/Nothing.h"
#include "../Util/Logger.h"

Parry::Parry()
{
    m_chain = NULL;
}

Parry::~Parry()
{
    delete m_chain;
}

void Parry::DetermineChain()
{
    if(m_state->m_memory->player_two_action == EDGE_HANGING)
    {
        CreateChain2(EdgeAction, STAND_UP);
        m_chain->PressButtons();
        return;
    }

    //Can we just dash out of range?
    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    int frames_left_start = m_state->firstHitboxFrame((CHARACTER)m_state->m_memory->player_one_character, (ACTION)m_state->m_memory->player_one_action)
        - m_state->m_memory->player_one_action_frame;

    int frames_left_end = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character, (ACTION)m_state->m_memory->player_one_action)
        - m_state->m_memory->player_one_action_frame;

    if((frames_left_start > 0 ||
        frames_left_end > 0) &&
        (m_state->m_memory->player_two_action == DASHING ||
        m_state->m_memory->player_two_action == STANDING ||
        m_state->m_memory->player_two_action == WALK_SLOW ||
        m_state->m_memory->player_two_action == TURNING))
    {
        //Do we have time to run away from the attack?
        if(frames_left_start <= 0 ||
            FOX_DASH_SPEED * frames_left_start > MARTH_FSMASH_RANGE - distance)
        {
            //Keep doing what we were doing before if we're turning
            if(m_state->m_memory->player_two_action == TURNING)
            {
                //Make a new Run chain, since it's always interruptible
                delete m_chain;
                m_chain = NULL;
                CreateChain2(Run, !m_state->m_memory->player_two_facing);
                m_chain->PressButtons();
                return;
            }

            //Dash back, since we're about to start running
            if(m_state->m_memory->player_two_action == DASHING &&
                m_state->m_memory->player_two_action_frame >= FOX_DASH_FRAMES-2)
            {
                //Make a new Run chain, since it's always interruptible
                delete m_chain;
                m_chain = NULL;
                CreateChain2(Run, !m_state->m_memory->player_two_facing);
                m_chain->PressButtons();
                return;
            }

            //Dash to the pivot point outside attack range
            bool onRight = m_state->m_memory->player_one_x > 0;
            double pivotPosition = m_state->m_memory->player_one_x + (onRight ? -MARTH_FSMASH_RANGE - 4 : MARTH_FSMASH_RANGE + 4);
            Logger::Instance()->Log(INFO, "Trying to run away to pivot point: " + std::to_string(pivotPosition) +
                " with: " + std::to_string(frames_left_start) + " frames left");

            //Make a new Run chain, since it's always interruptible
            delete m_chain;
            m_chain = NULL;
            bool left_of_pivot_position = m_state->m_memory->player_two_x < pivotPosition;
            CreateChain2(Run, left_of_pivot_position);
            m_chain->PressButtons();
            return;
        }
    }

    //TODO: SWORD_DANCE_4_LOW is a multi-hit attack. Let's handle that differently. Maybe just light shield
    if(m_state->m_memory->player_one_action == ACTION::GRAB ||
        m_state->m_memory->player_one_action == ACTION::GRAB_RUNNING)
    {
        CreateChain(SpotDodge);
        m_chain->PressButtons();
    }
    //We're assuming there's no other grab-type attacks. (Yoshi's neutral-b for instance)
    else
    {
        CreateChain(Powershield);
        m_chain->PressButtons();
    }
}
