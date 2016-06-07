#include <typeinfo>
#include <math.h>
#include <cmath>

#include "TechChase.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"
#include "../Chains/Nothing.h"
#include "../Chains/Run.h"
#include "../Chains/Walk.h"
#include "../Chains/Wavedash.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/GrabAndThrow.h"
#include "../Chains/Jab.h"
#include "../Chains/DashDance.h"

TechChase::TechChase()
{
    m_roll_position = 0;
    m_pivotPosition = 0;
    m_chain = NULL;
}

TechChase::~TechChase()
{
    delete m_chain;
}

void TechChase::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    bool player_two_is_to_the_left = (m_state->m_memory->player_one_x > m_state->m_memory->player_two_x);

    //If our opponent is just lying there, go dash around the pivot point and wait
    if(m_state->m_memory->player_one_action == LYING_GROUND_UP ||
        m_state->m_memory->player_one_action == LYING_GROUND_DOWN ||
        m_state->m_memory->player_one_action == TECH_MISS_UP ||
        m_state->m_memory->player_one_action == TECH_MISS_DOWN)
    {
        bool isLeft = m_state->m_memory->player_one_x < 0;
        int pivot_offset = isLeft ? 20 : -20;
        m_pivotPosition = m_state->m_memory->player_one_x + pivot_offset;

        CreateChain3(DashDance, m_pivotPosition, 0);
        m_chain->PressButtons();
        return;
    }

    uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    int frames_left = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

    //If they're vulnerable, go punish it
    if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) ||
        (m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_action_frame > lastHitboxFrame))
    {
        //Figure out where they will stop rolling, only on the first frame
        if(m_roll_position == 0)
        {
            double rollDistance = m_state->getRollDistance((CHARACTER)m_state->m_memory->player_one_character,
                (ACTION)m_state->m_memory->player_one_action);

            bool directon = m_state->getRollDirection((ACTION)m_state->m_memory->player_one_action);

            if(m_state->m_memory->player_one_facing == directon)
            {
                m_roll_position = m_state->m_rollStartPosition + rollDistance;
            }
            else
            {
                m_roll_position = m_state->m_rollStartPosition - rollDistance;
            }

            //TODO: Needs to account for how much enemy will slide from the START of the roll. Not here.
            //Calculate how much the enemy will slide
            double enemySpeed = m_state->m_memory->player_one_speed_x_attack;

            double slidingAdjustmentEnemy = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character, enemySpeed, frames_left);
            m_roll_position += slidingAdjustmentEnemy;

            Logger::Instance()->Log(INFO, "enemySpeed: " + std::to_string(enemySpeed));
            Logger::Instance()->Log(INFO, "slidingAdjustmentEnemy: " + std::to_string(slidingAdjustmentEnemy));

            //Roll position can't be off the stage
            if(m_roll_position > m_state->getStageEdgeGroundPosition())
            {
                m_roll_position = m_state->getStageEdgeGroundPosition();
            }
            else if (m_roll_position < (-1) * m_state->getStageEdgeGroundPosition())
            {
                m_roll_position = (-1) * m_state->getStageEdgeGroundPosition();
            }

            //If the opponent is attacking, set their roll position to be where they're at now (not the last roll)
            if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
            {
                m_roll_position = m_state->m_memory->player_one_x;
            }

            if(player_two_is_to_the_left)
            {
                m_pivotPosition = m_roll_position - FOX_GRAB_RANGE;
            }
            else
            {
                m_pivotPosition = m_roll_position + FOX_GRAB_RANGE;
            }
        }

        int frameDelay = 7;
        double distance;
        if(m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING)
        {
            //We have to jump cancel the grab. So that takes an extra frame
            frameDelay++;
        }

        double slidingAdjustment = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_two_character,
            m_state->m_memory->player_two_speed_ground_x_self, frameDelay);

        distance = std::abs(m_roll_position - (m_state->m_memory->player_two_x + slidingAdjustment));

        Logger::Instance()->Log(INFO, "slidingAdjustment: " + std::to_string(slidingAdjustment));
        Logger::Instance()->Log(INFO, "distance: " + std::to_string(distance));

        //If we're too late, at least get close
        if(frames_left < frameDelay)
        {
            bool to_the_left = m_roll_position > m_state->m_memory->player_two_x;
            Logger::Instance()->Log(INFO, "Trying to tech chase but can't make it in time...");
            CreateChain2(Run, to_the_left);
            m_chain->PressButtons();
            return;
        }

        Logger::Instance()->Log(INFO, "Trying to tech chase a roll at position: " + std::to_string(m_roll_position) +
            " with: " + std::to_string(frames_left) + " frames left");

        //How many frames of vulnerability are there at the tail end of the animation?
        int vulnerable_frames = 7;
        if(m_state->m_memory->player_one_action == EDGE_GETUP_QUICK)
        {
            vulnerable_frames = 2;
        }
        if(m_state->m_memory->player_one_action == EDGE_GETUP_SLOW)
        {
            vulnerable_frames = 3;
        }
        if(m_state->m_memory->player_one_action == MARTH_COUNTER)
        {
            vulnerable_frames = 59;
        }

        bool facingRight = m_state->m_memory->player_two_facing;
        if(m_state->m_memory->player_two_action == TURNING)
        {
            facingRight = !facingRight;
        }

        bool to_the_left = m_roll_position > m_state->m_memory->player_two_x;
        //Given sliding, are we going to be behind the enemy?
        bool behindEnemy = (m_roll_position < (m_state->m_memory->player_two_x + slidingAdjustment)) == m_state->m_memory->player_two_facing;
        Logger::Instance()->Log(INFO, "behindEnemy: " + std::to_string(behindEnemy));

        //Can we grab the opponent right now?
        if(frames_left - frameDelay >= 0 &&
            frames_left - frameDelay <= vulnerable_frames &&
            distance < FOX_GRAB_RANGE &&
            to_the_left == facingRight &&
            !behindEnemy &&
            m_state->m_memory->player_one_action != TECH_MISS_UP && //Don't try to grab when they miss a tech, it doesn't work
            m_state->m_memory->player_one_action != TECH_MISS_DOWN)
        {
            CreateChain2(GrabAndThrow, DOWN_THROW);
            m_chain->PressButtons();
            return;
        }
        else
        {
            //If they're right in front of us and we're not already running, then just hang out and wait
            if(m_state->m_memory->player_two_action != DASHING &&
                m_state->m_memory->player_two_action != RUNNING &&
                m_state->m_memory->player_two_action != TURNING &&
                distance < FOX_GRAB_RANGE &&
                to_the_left == m_state->m_memory->player_two_facing)
            {
                CreateChain(Nothing);
                m_chain->PressButtons();
                return;
            }

            //Make a new Run chain, since it's always interruptible
            delete m_chain;
            m_chain = NULL;
            bool left_of_pivot_position = m_state->m_memory->player_two_x < m_pivotPosition;
            CreateChain2(Run, left_of_pivot_position);
            m_chain->PressButtons();
            return;
        }
    }

    //Default to dashing at the opponent
    CreateChain3(DashDance, m_state->m_memory->player_one_x, 0);
    m_chain->PressButtons();
    return;
}
