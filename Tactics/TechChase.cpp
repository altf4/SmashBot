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

    uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    int frames_left = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

    int totalFrames = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    double distance = std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x);

    //Is it safe to wavedash in after shielding the attack?
    //  Don't wavedash off the edge of the stage
    //  And don't bother if we're already in grab range. (Just grab them)
    if(frames_left > 15 &&
        distance > FOX_GRAB_RANGE &&
        m_state->m_memory->player_two_action == SHIELD_RELEASE &&
        (m_state->getStageEdgeGroundPosition() > std::abs(m_state->m_memory->player_two_x) + 10))
    {
        CreateChain2(Wavedash, player_two_is_to_the_left);
        m_chain->PressButtons();
        return;
    }

    //If our opponent is just lying there, go dash around the pivot point and wait
    if(m_state->m_memory->player_one_action == LYING_GROUND_UP ||
        m_state->m_memory->player_one_action == LYING_GROUND_DOWN ||
        m_state->m_memory->player_one_action == TECH_MISS_UP ||
        m_state->m_memory->player_one_action == TECH_MISS_DOWN)
    {
        bool isRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;

        //If opponent missed a tech right nearby us, just walk in close.
        if(distance < 25 &&
            m_state->m_memory->player_two_action != DASHING &&
            m_state->m_memory->player_two_action != RUNNING)
        {
            bool onInnerStage = std::abs(m_state->m_memory->player_two_x) < m_state->getStageEdgeGroundPosition() - FOX_GRAB_RANGE;
            bool nearRightEdge = m_state->m_memory->player_two_x > 0;
            bool facingEdge = nearRightEdge == m_state->m_memory->player_two_facing;

            //Walk in if they're getting too far away, or if they're behind us
            //But if we've already backed them into a corner, don't go further
            if((distance > 7 &&
                (onInnerStage || !facingEdge)) ||
                isRight == m_state->m_memory->player_two_facing)
            {
                CreateChain2(Walk, !isRight);
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

        //try to pivot away from the enemy, unless that would put us off the stage
        int pivot_offset = isRight ? 20 : -20;
        if(std::abs(m_state->m_memory->player_two_x + pivot_offset) > m_state->getStageEdgeGroundPosition())
        {
            pivot_offset = isRight ? -20 : 20;
        }
        m_pivotPosition = m_state->m_memory->player_one_x + pivot_offset;

        CreateChain3(DashDance, m_pivotPosition, 0);
        m_chain->PressButtons();
        return;
    }

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

            //Calculate how much the enemy will slide
            double enemySpeed = m_state->m_rollStartSpeed;

            double slidingAdjustmentEnemy = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character, enemySpeed, totalFrames);
            m_roll_position += slidingAdjustmentEnemy;

            //Don't adjust for self sliding if the enemy is in a roll. That distance is already accounted for
            if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) ||
                m_state->m_memory->player_one_action == MARTH_COUNTER)
            {
                double enemySelfSlide = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_one_character,
                    m_state->m_rollStartSpeedSelf, totalFrames);
                m_roll_position += enemySelfSlide;
            }

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
        double distanceFromRoll;
        if(m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING ||
            m_state->m_memory->player_two_action == SHIELD_RELEASE)
        {
            //We have to jump cancel the grab. So that takes an extra frame
            frameDelay++;
        }

        double slidingAdjustment = m_state->calculateSlideDistance((CHARACTER)m_state->m_memory->player_two_character,
            m_state->m_memory->player_two_speed_ground_x_self, frameDelay);

        distanceFromRoll = std::abs(m_roll_position - (m_state->m_memory->player_two_x + slidingAdjustment));

        Logger::Instance()->Log(INFO, "Trying to tech chase a roll at position: " + std::to_string(m_roll_position) +
            " with: " + std::to_string(frames_left) + " frames left");

        //How many frames of vulnerability are there at the tail end of the animation?
        int vulnerable_frames = m_state->trailingVulnerableFrames((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action);

        //Except for marth counter. You can always grab that
        if(m_state->m_memory->player_one_action == MARTH_COUNTER)
        {
            vulnerable_frames = 59;
        }
        //If the opponent is attacking, they don't have invulnerability like rolls do
        //Except getup attack, which is both a roll and an attack
        if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
            m_state->m_memory->player_one_action != GETUP_ATTACK &&
            m_state->m_memory->player_one_action != GROUND_ATTACK_UP)
        {
            vulnerable_frames = totalFrames;
        }

        bool facingRight = m_state->m_memory->player_two_facing;
        if(m_state->m_memory->player_two_action == TURNING)
        {
            facingRight = !facingRight;
        }

        bool to_the_left = m_roll_position > m_state->m_memory->player_two_x;
        //Given sliding, are we going to be behind the enemy?
        bool behindEnemy = (m_roll_position < (m_state->m_memory->player_two_x + slidingAdjustment)) == m_state->m_memory->player_two_facing;

        //Can we grab the opponent right now?
        if(frames_left - frameDelay >= 0 &&
            frames_left - frameDelay <= vulnerable_frames &&
            distanceFromRoll < FOX_GRAB_RANGE &&
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
            double currentDistance = std::abs(m_roll_position - m_state->m_memory->player_two_x);

            //If they're right in front of us and we're not already running, then just hang out and wait
            if(m_state->m_memory->player_two_action != DASHING &&
                m_state->m_memory->player_two_action != RUNNING &&
                m_state->m_memory->player_two_action != TURNING &&
                distanceFromRoll < FOX_GRAB_RANGE)
            {
                //If the target location is right behind us, just turn around, don't run
                // Also, if it's all the same, just get a little closer than we probably need.
                // Sometimes grab is shorter range than we'd like
                if(to_the_left != m_state->m_memory->player_two_facing ||
                    distanceFromRoll > FOX_GRAB_RANGE/2)
                {
                    CreateChain2(Walk, to_the_left);
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

            //If we're sure we'll have time (Like when we have lots of vulnerable frames) dash dance right at the edge of range
            //Default to dashing at the opponent
            if(vulnerable_frames >= 7 &&
                m_state->m_memory->player_one_action != FORWARD_TECH &&
                m_state->m_memory->player_one_action != BACKWARD_TECH)
            {
                bool isRight = m_roll_position < m_state->m_memory->player_two_x;
                int pivot_offset = isRight ? FOX_JC_GRAB_MAX_SLIDE : -FOX_JC_GRAB_MAX_SLIDE;
                //Don't anchor our dash dance off the stage
                if(std::abs(m_roll_position + pivot_offset) > m_state->getStageEdgeGroundPosition())
                {
                    pivot_offset = isRight ? -FOX_JC_GRAB_MAX_SLIDE : FOX_JC_GRAB_MAX_SLIDE;
                }
                m_pivotPosition = m_roll_position + pivot_offset;
                CreateChain3(DashDance, m_pivotPosition, 0);
                m_chain->PressButtons();
                return;
            }

            //How many frames do we have to wait until we can just dash in there and grab in one go.
            //Tech roll is the longest roll and we can just barely make that with 0 frames of waiting. So
            //this should always be possible

            //This is the number of frames we're going to need to run the distance until we're in range
            int travelFrames = (currentDistance - FOX_GRAB_RANGE - FOX_JC_GRAB_MAX_SLIDE) / FOX_DASH_SPEED;

            //Account for the startup frames, too
            if(m_state->m_memory->player_two_action != DASHING &&
                m_state->m_memory->player_two_action != RUNNING)
            {
                travelFrames++;
            }
            if(to_the_left != facingRight)
            {
                travelFrames++;
            }

            //This is the most frames we can wait before we need to leave.
            int maxWaitFrames = frames_left - travelFrames - 8;
            //This is the smallest number of frames we have to wait or else we'll get there too early.
            int minWaitFrames = maxWaitFrames - vulnerable_frames;
            int midWaitFrames = (maxWaitFrames + minWaitFrames) / 2;

            //If the enemy is just beyond our reach, then we should just walk forward a little. Don't dash or we'll slide past it
            if((m_state->m_memory->player_two_action == STANDING ||
                m_state->m_memory->player_two_action == WALK_SLOW ||
                m_state->m_memory->player_two_action == WALK_MIDDLE) &&
                currentDistance > FOX_GRAB_RANGE &&
                currentDistance < FOX_GRAB_RANGE + FOX_JC_GRAB_MAX_SLIDE)
            {
                CreateChain2(Walk, to_the_left);
                m_chain->PressButtons();
                return;
            }

            if(midWaitFrames > 0)
            {
                //If we're dashing, we will need to do a turn around
                if(m_state->m_memory->player_two_action == DASHING)
                {
                    delete m_chain;
                    m_chain = NULL;
                    CreateChain2(Run, !m_state->m_memory->player_two_facing);
                    m_chain->PressButtons();
                    return;
                }
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
