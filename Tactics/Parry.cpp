#include <cmath>
#include <typeinfo>

#include "Parry.h"
#include "../Util/Constants.h"
#include "../Chains/Powershield.h"
#include "../Chains/SpotDodge.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/Run.h"
#include "../Chains/Walk.h"
#include "../Chains/DashDance.h"
#include "../Chains/HoldShield.h"
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
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

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

    bool onRight = m_state->m_memory->player_two_x > m_state->m_memory->player_one_x;

    //If the enemy is doing a getup attack, let's handle that separately.
    //Normally we'd try to powershield it, but in this case we REALLY want to be in grab range
    // when the attack is finished. So let's make sure that happens.
    if(m_state->m_memory->player_one_action == GROUND_ATTACK_UP)
    {
        //Are we in range? If so, powershield then hold down
        if(frames_left_start > 2)
        {
            //If we try walkig at them any closer, we can walk PAST
            if(distance > 3)
            {
                //Just walk in
                delete m_chain;
                m_chain = NULL;
                CreateChain2(Walk, !onRight);
                m_chain->PressButtons();
                return;
            }
            else
            {
                CreateChain(Nothing);
                m_chain->PressButtons();
                return;
            }
        }
        else
        {
            //Plus 4 frames due to hit stun
            CreateChain2(HoldShield, frames_left_end+4);
            m_chain->PressButtons();
            return;
        }
    }

    //TODO: This is really kludgey and horrible. Replace this eventually with the solution to:
    // https://github.com/altf4/SmashBot/issues/58
    bool isUnderDolphinSlash = m_state->m_memory->player_one_y < m_state->m_memory->player_two_y &&
        m_state->m_memory->player_one_action == UP_B &&
        std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x) < 25;

    if((frames_left_start > 0 || frames_left_end > 0) &&
        !isUnderDolphinSlash &&
        (m_state->m_memory->player_two_action == DASHING ||
        m_state->m_memory->player_two_action == STANDING ||
        m_state->m_memory->player_two_action == WALK_SLOW ||
        m_state->m_memory->player_two_action == TURNING))
    {
        //Do we have time to run away from the attack?
        if(FOX_DASH_SPEED * frames_left_start > MARTH_FSMASH_RANGE - distance)
        {
            //Dash to the pivot point outside attack range
            bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
            double pivotPosition = m_state->m_memory->player_one_x + (onRight ? MARTH_FSMASH_RANGE - 4 : -MARTH_FSMASH_RANGE + 4);
            Logger::Instance()->Log(INFO, "Trying to run away to pivot point: " + std::to_string(pivotPosition) +
                " with: " + std::to_string(frames_left_start) + " frames left");

            delete m_chain;
            m_chain = NULL;
            CreateChain3(DashDance, pivotPosition, 0);
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
