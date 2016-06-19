#include <typeinfo>
#include <math.h>
#include <cmath>

#include "Punish.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"
#include "../Chains/SmashAttack.h"
#include "../Chains/Nothing.h"
#include "../Chains/Run.h"
#include "../Chains/Walk.h"
#include "../Chains/Wavedash.h"
#include "../Chains/EdgeAction.h"

Punish::Punish()
{
    m_endPosition = 0;
    m_chain = NULL;
}

Punish::~Punish()
{
    delete m_chain;
}

void Punish::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    //If we're hanging on the egde, and they are falling above the stage, stand up
    if(m_state->m_memory->player_one_action == DEAD_FALL &&
        m_state->m_memory->player_two_action == EDGE_HANGING &&
        std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + .001)
    {
        CreateChain2(EdgeAction, STAND_UP);
        m_chain->PressButtons();
        return;
    }

    bool player_two_is_to_the_left = (m_state->m_memory->player_one_x > m_state->m_memory->player_two_x);

    int totalFrames = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);
    int frames_left = totalFrames - m_state->m_memory->player_one_action_frame;

    if(m_state->isDamageState((ACTION)m_state->m_memory->player_one_action))
    {
        frames_left = m_state->m_memory->player_one_hitstun_frames_left;
    }

    //Are we before an attack?
    if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
    {
        if(m_state->m_memory->player_one_action_frame < m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action))
        {
            frames_left = m_state->firstHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
                (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;
        }
    }

    double enemyHitSlide = 0;
    double enemySelfSlide = 0;

    //Figure out where they will stop, only on the first frame
    if(m_endPosition == 0)
    {
        //We're assuming that the opponent is vulnerable for some duration of time
        //Where will the opponent be at the end of their vulnerable state?
        if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action))
        {
            double rollDistance = m_state->getRollDistance((CHARACTER)m_state->m_memory->player_one_character,
                (ACTION)m_state->m_memory->player_one_action);

            bool directon = m_state->getRollDirection((ACTION)m_state->m_memory->player_one_action);
            if(m_state->m_memory->player_one_facing == directon)
            {
                m_endPosition = m_state->m_rollStartPosition + rollDistance;
            }
            else
            {
                m_endPosition = m_state->m_rollStartPosition - rollDistance;
            }

            //Calculate hit sliding from the START of the roll.
            enemyHitSlide = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character,
                m_state->m_rollStartSpeed, totalFrames);
            m_endPosition += enemyHitSlide;

        }
        else
        {
            m_endPosition = m_state->m_memory->player_one_x;
            enemySelfSlide = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character,
                m_state->m_memory->player_one_speed_ground_x_self, frames_left);
            m_endPosition += enemySelfSlide;

            enemyHitSlide = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character,
                m_state->m_memory->player_one_speed_x_attack, frames_left);
            m_endPosition += enemyHitSlide;
        }

        //You can't roll off the stage
        if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action))
        {
            if(m_endPosition > m_state->getStageEdgeGroundPosition())
            {
                m_endPosition = m_state->getStageEdgeGroundPosition();
            }
            else if (m_endPosition < (-1) * m_state->getStageEdgeGroundPosition())
            {
                m_endPosition = (-1) * m_state->getStageEdgeGroundPosition();
            }
        }
    }

    //Take our sliding into account, assuming we started an attack this frame
    double selfSlide = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_two_character,
        m_state->m_memory->player_two_speed_ground_x_self, frames_left);

    double ourEndPosition = m_state->m_memory->player_two_x + selfSlide;

    //Calculate distance between players
    double distance = std::abs(m_endPosition - ourEndPosition);

    Logger::Instance()->Log(INFO, "Trying to punish at position: " + std::to_string(m_endPosition) +
        " with: " + std::to_string(frames_left) + " frames left");

    //It takes 7 frames to get the upsmash hitbox out
    int frameDelay = 7;
    //If we have to jump cancel, then that takes an extra frame
    if(m_state->m_memory->player_two_action == DASHING ||
        m_state->m_memory->player_two_action == SHIELD ||
        m_state->m_memory->player_two_action == SHIELD_RELEASE ||
        m_state->m_memory->player_two_action == RUNNING ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND)
    {
        frameDelay++;
    }

    bool to_the_left = m_endPosition > ourEndPosition;

    //Are we facing the right way, are in range, and have time to upsmash? Then do it.
    if(frames_left - frameDelay >= 0 &&
        distance < FOX_UPSMASH_RANGE_NEAR &&
        to_the_left == m_state->m_memory->player_two_facing)
    {
        CreateChain3(SmashAttack, SmashAttack::UP, std::max(0, frames_left - frameDelay - 1));
        m_chain->PressButtons();
        return;
    }
    else
    {
        //If the target location is right behind us, just turn around, don't run
        if(distance < FOX_UPSMASH_RANGE_NEAR &&
            to_the_left != m_state->m_memory->player_two_facing &&
            m_state->m_memory->player_two_action != DASHING &&
            m_state->m_memory->player_two_action != RUNNING)
        {
            CreateChain2(Walk, to_the_left);
            m_chain->PressButtons();
            return;
        }

        bool needsWavedash = m_state->m_memory->player_two_action == SHIELD_RELEASE ||
            m_state->m_memory->player_two_action == SHIELD||
            m_state->m_memory->player_two_action == DOWN_B_GROUND;

        //Do we need to wavedash?
        if(distance > FOX_UPSMASH_RANGE_NEAR &&
            frames_left > WAVEDASH_FRAMES &&
             needsWavedash)
        {
            CreateChain2(Wavedash, player_two_is_to_the_left);
            m_chain->PressButtons();
            return;
        }

        //Default to just running at our opponent
        CreateChain2(Run, to_the_left);
        m_chain->PressButtons();
        return;
    }
}
