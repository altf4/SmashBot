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

    //Dash back, since we're about to start running
    //UNLESS we're trying to tech chase a tech roll. Then we don't have enough time to dash back
    if(m_state->m_memory->player_two_action == DASHING &&
        m_state->m_memory->player_two_action_frame >= FOX_DASH_FRAMES-2 &&
        m_state->m_memory->player_one_action != FORWARD_TECH &&
        m_state->m_memory->player_one_action != BACKWARD_TECH)
    {
        //Make a new Run chain, since it's always interruptible
        delete m_chain;
        m_chain = NULL;
        CreateChain2(Run, !m_state->m_memory->player_two_facing);
        m_chain->PressButtons();
        return;
    }

    //If our opponent is just lying there, go dash around the pivot point and wait
    if(m_state->m_memory->player_one_action == LYING_GROUND_UP ||
      m_state->m_memory->player_one_action == TECH_MISS_UP ||
      m_state->m_memory->player_one_action == TECH_MISS_DOWN)
    {
        bool isLeft = m_state->m_memory->player_one_x < 0;
        int pivot_offset = isLeft ? 20 : -20;
        m_pivotPosition = m_state->m_memory->player_one_x + pivot_offset;

        //Make a new Run chain, since it's always interruptible
        delete m_chain;
        m_chain = NULL;
        bool left_of_pivot_position = m_state->m_memory->player_two_x < m_pivotPosition;
        CreateChain2(Run, left_of_pivot_position);
        m_chain->PressButtons();
        return;
    }

    uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    //If they're vulnerable, go punish it
    if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) ||
        (m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
            m_state->m_memory->player_one_action_frame > lastHitboxFrame))
    {
        //Figure out where they will stop rolling, only on the first frame
        if(m_roll_position == 0)
        {
            switch(m_state->m_memory->player_one_action)
            {
                case ROLL_FORWARD:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_ROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_ROLL_DISTANCE;
                    }
                    break;
                }
                case ROLL_BACKWARD:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_ROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_ROLL_DISTANCE;
                    }
                    break;
                }
                case EDGE_ROLL_SLOW:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_EDGE_ROLL_DISTANCE ;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_EDGE_ROLL_DISTANCE;
                    }
                    break;
                }
                case EDGE_ROLL_QUICK:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_EDGE_ROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_EDGE_ROLL_DISTANCE;
                    }
                    break;
                }
                case EDGE_GETUP_QUICK:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_GETUP_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_GETUP_DISTANCE;
                    }
                    break;
                }
                case EDGE_GETUP_SLOW:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_GETUP_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_GETUP_DISTANCE;
                    }
                    break;
                }
                case FORWARD_TECH:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_TECHROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_TECHROLL_DISTANCE;
                    }
                    break;
                }
                case BACKWARD_TECH:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_TECHROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_TECHROLL_DISTANCE;
                    }
                    break;
                }
                case GROUND_ROLL_FORWARD:
                case GROUND_ROLL_FORWARD_OTHER:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_GROUND_FORWARD_ROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_GROUND_FORWARD_ROLL_DISTANCE;
                    }
                    break;
                }
                case GROUND_ROLL_BACKWARD:
                case GROUND_ROLL_BACKWARD_OTHER:
                {
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_rollStartPosition - MARTH_GROUND_BACK_ROLL_DISTANCE;
                    }
                    else
                    {
                        m_roll_position = m_state->m_rollStartPosition + MARTH_GROUND_BACK_ROLL_DISTANCE;
                    }
                    break;
                }
                default:
                {
                    m_roll_position = m_state->m_rollStartPosition;
                    break;
                }
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

        bool to_the_left = m_roll_position > m_state->m_memory->player_two_x;

        int frames_left = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

        int frameDelay = 7;
        double distance;
        if(m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING)
        {
            double slidingAdjustment = frameDelay * (std::abs(m_state->m_memory->player_two_speed_ground_x_self));
            distance = std::abs(std::abs(m_roll_position - m_state->m_memory->player_two_x) - slidingAdjustment);
        }
        else
        {
            distance = std::abs(m_roll_position - m_state->m_memory->player_two_x);
        }

        //If we're too late, at least get close
        if(frames_left < frameDelay)
        {
            Logger::Instance()->Log(INFO, "Trying to tech chase but can't make it in time...");
            CreateChain2(Run, to_the_left);
            m_chain->PressButtons();
            return;
        }

        Logger::Instance()->Log(INFO, "Trying to tech chase a roll at position: " + std::to_string(m_roll_position) +
            " with: " + std::to_string(frames_left) + " frames left");

        //How many frames of vulnerability are there at the tail end of the animation?
        int vulnerable_frames = 7;
        if(m_state->m_memory->player_one_action == MARTH_COUNTER)
        {
            vulnerable_frames = 59;
        }

        //Can we grab the opponent right now?
        if(frames_left - frameDelay >= 0 &&
            frames_left - frameDelay <= vulnerable_frames &&
            distance < FOX_GRAB_RANGE &&
            to_the_left == m_state->m_memory->player_two_facing &&
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

    //Default to walking in towards the player
    //Make a new Run chain, since it's always interruptible
    delete m_chain;
    m_chain = NULL;
    CreateChain2(Run, player_two_is_to_the_left);
    m_chain->PressButtons();
    return;
}
