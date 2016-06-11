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

    //If the enemy is doing a getup attack, let's handle that separately.
    //Normally we'd try to powershield it, but in this case we REALLY want to be in grab range
    // when the attack is finished. So let's make sure that happens.
    if(m_state->m_memory->player_one_action == GETUP_ATTACK ||
        m_state->m_memory->player_one_action == GROUND_ATTACK_UP)
    {
        //Are we in range? If so, hold down on shield

        //Speed takes an initial hit of 1.22 as soon as you shield ONLY if you're dashing. Take that into account
        double predictedInitSpeed = m_state->m_memory->player_two_speed_ground_x_self;
        double slidingAdjustment = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_two_character,
            predictedInitSpeed, frames_left_start);
        double predictedStopPoint = m_state->m_memory->player_two_x + slidingAdjustment;

        if(m_state->m_memory->player_two_action == DASHING)
        {
            if(m_state->m_memory->player_two_speed_ground_x_self > 0)
            {
                predictedInitSpeed = std::max(0.0, m_state->m_memory->player_two_speed_ground_x_self - 1.22);
            }
            else
            {
                predictedInitSpeed = std::min(0.0, m_state->m_memory->player_two_speed_ground_x_self + 1.22);
            }

            slidingAdjustment = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_two_character,
                predictedInitSpeed, frames_left_start);

            //One frame will be used to just continue dashing, then we slide
            predictedStopPoint = m_state->m_memory->player_two_x + slidingAdjustment +
                m_state->m_memory->player_two_speed_ground_x_self;
        }

        double predictedDistance = std::abs(predictedStopPoint - m_state->m_memory->player_one_x);
        bool onRight = m_state->m_memory->player_two_x > m_state->m_memory->player_one_x;

        //Make sure we don't go PAST the opponent
        if(onRight == (predictedStopPoint > m_state->m_memory->player_one_x))
        {
            //Be a third of the grab range in, to be sure we won't be pushed out of range
            if(predictedDistance < (double)FOX_GRAB_RANGE/(3.0))
            {
                //Plus 4 frames due to hit stun
                CreateChain2(HoldShield, frames_left_end+4);
                m_chain->PressButtons();
                return;
            }

            //Run in!
            delete m_chain;
            m_chain = NULL;
            CreateChain2(Run, !onRight);
            m_chain->PressButtons();
            return;
        }

        //We're going to go past our opponent. Oh no!
        //Can we walk?
        if(m_state->m_memory->player_two_action != DASHING &&
            m_state->m_memory->player_two_action != RUNNING)
        {
            delete m_chain;
            m_chain = NULL;
            CreateChain2(Walk, !onRight);
            m_chain->PressButtons();
            return;
        }
        else
        {
            //Try dashing away. Pivot shield ought to work
            //Make a new Run chain, since it's always interruptible
            delete m_chain;
            m_chain = NULL;
            CreateChain2(Run, !m_state->m_memory->player_two_facing);
            m_chain->PressButtons();
            return;
        }
    }

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
            //Dash to the pivot point outside attack range
            bool onRight = m_state->m_memory->player_one_x > 0;
            double pivotPosition = m_state->m_memory->player_one_x + (onRight ? -MARTH_FSMASH_RANGE - 4 : MARTH_FSMASH_RANGE + 4);
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
