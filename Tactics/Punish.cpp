#include <typeinfo>
#include <math.h>
#include <cmath>

#include "Punish.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"
#include "../Chains/SmashAttack.h"
#include "../Chains/Nothing.h"
#include "../Chains/Jab.h"
#include "../Chains/Run.h"
#include "../Chains/Walk.h"
#include "../Chains/Wavedash.h"
#include "../Chains/EdgeAction.h"

Punish::Punish()
{
    m_roll_position = 0;
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

    //If they're rolling, go punish it where they will stop
    if(m_state->m_memory->player_one_action == ROLL_FORWARD ||
        m_state->m_memory->player_one_action == ROLL_BACKWARD ||
        m_state->m_memory->player_one_action == EDGE_ROLL_SLOW ||
        m_state->m_memory->player_one_action == EDGE_ROLL_QUICK ||
        m_state->m_memory->player_one_action == EDGE_GETUP_QUICK ||
        m_state->m_memory->player_one_action == EDGE_GETUP_SLOW)
    {
        //Figure out where they will stop rolling, only on the first frame
        if(m_roll_position == 0)
        {
            //Scale the offset depending on how far into the roll they are
            //TODO: This is not strictly linear. But let's assume it is and maybe it will work well enough
            double scale = 1;
            switch(m_state->m_memory->player_one_action)
            {
                case ROLL_FORWARD:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_ROLL_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_ROLL_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_ROLL_DISTANCE * scale;
                    }
                    break;
                }
                case ROLL_BACKWARD:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_ROLL_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_ROLL_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_ROLL_DISTANCE * scale;
                    }
                    break;
                }
                case EDGE_ROLL_SLOW:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_EDGE_ROLL_SLOW_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_EDGE_ROLL_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_EDGE_ROLL_DISTANCE * scale;
                    }
                    break;
                }
                case EDGE_ROLL_QUICK:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_EDGE_ROLL_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_EDGE_ROLL_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_EDGE_ROLL_DISTANCE * scale;
                    }
                    break;
                }
                case EDGE_GETUP_QUICK:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_EDGE_GETUP_QUICK_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_GETUP_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_GETUP_DISTANCE * scale;
                    }
                    break;
                }
                case EDGE_GETUP_SLOW:
                {
                    scale = 1 - ((double)(m_state->m_memory->player_one_action_frame - 1) / (double)MARTH_EDGE_GETUP_SLOW_FRAMES);
                    if(m_state->m_memory->player_one_facing)
                    {
                        m_roll_position = m_state->m_memory->player_one_x + MARTH_GETUP_DISTANCE * scale;
                    }
                    else
                    {
                        m_roll_position = m_state->m_memory->player_one_x - MARTH_GETUP_DISTANCE * scale;
                    }
                    break;
                }
            }

            if(m_roll_position > m_state->getStageEdgeGroundPosition())
            {
                m_roll_position = m_state->getStageEdgeGroundPosition();
            }
            else if (m_roll_position < (-1) * m_state->getStageEdgeGroundPosition())
            {
                m_roll_position = (-1) * m_state->getStageEdgeGroundPosition();
            }
        }

        int frames_left;
        if(m_state->m_memory->player_one_action == ROLL_FORWARD ||
            m_state->m_memory->player_one_action == ROLL_BACKWARD)
        {
            frames_left = MARTH_ROLL_FRAMES - m_state->m_memory->player_one_action_frame;
        }
        else if(m_state->m_memory->player_one_action == EDGE_ROLL_SLOW)
        {
            frames_left = MARTH_EDGE_ROLL_SLOW_FRAMES - m_state->m_memory->player_one_action_frame;
        }
        else if(m_state->m_memory->player_one_action == EDGE_ROLL_QUICK)
        {
            frames_left = MARTH_EDGE_ROLL_FRAMES - m_state->m_memory->player_one_action_frame;
        }
        else if(m_state->m_memory->player_one_action == EDGE_GETUP_QUICK)
        {
            frames_left = MARTH_EDGE_GETUP_QUICK_FRAMES - m_state->m_memory->player_one_action_frame;
        }
        else if(m_state->m_memory->player_one_action == EDGE_GETUP_SLOW)
        {
            frames_left = MARTH_EDGE_GETUP_SLOW_FRAMES - m_state->m_memory->player_one_action_frame;
        }

        if(frames_left <= 7)
        {
            CreateChain(Nothing);
            m_chain->PressButtons();
            return;
        }

        //Upsmash if we're in range and facing the right way
        //  Factor in sliding during the smash animation
        double distance;
        int frameDelay = 8; //Frames until the first smash hitbox, plus one for leeway
        if(m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING)
        {
            double slidingAdjustment = 12.25 * (std::abs(m_state->m_memory->player_two_speed_ground_x_self));
            distance = std::abs(std::abs(m_roll_position - m_state->m_memory->player_two_x) - slidingAdjustment);
            frameDelay += 4;
        }
        else
        {
            distance = std::abs(m_roll_position - m_state->m_memory->player_two_x);
        }

        Logger::Instance()->Log(INFO, "Trying to punish a roll at position: " + std::to_string(m_roll_position) +
            " with: " + std::to_string(frames_left) + " frames left");

        bool to_the_left = m_roll_position > m_state->m_memory->player_two_x;
        if(frames_left >= frames_left &&
            distance < FOX_UPSMASH_RANGE_NEAR &&
            to_the_left == m_state->m_memory->player_two_facing)
        {
            CreateChain3(SmashAttack, SmashAttack::UP, std::max(0, frames_left - frameDelay));
            m_chain->PressButtons();
            return;
        }
        else
        {
            //If the target location is right behind us, just turn around, don't run
            if(distance < FOX_UPSMASH_RANGE_NEAR &&
                to_the_left != m_state->m_memory->player_two_facing)
            {
                CreateChain2(Walk, to_the_left);
                m_chain->PressButtons();
                return;
            }
            else
            {
                CreateChain2(Run, to_the_left);
                m_chain->PressButtons();
                return;
            }
        }
    }

    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    //How many frames do we have until we need to do something?
    int frames_left;
    //Are we before the attack or after?
    if(m_state->m_memory->player_one_action_frame < m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action))
    {
        //Before
        frames_left = m_state->firstHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame - 1;
        Logger::Instance()->Log(INFO, "Frames until first hitbox of the attack: " + std::to_string(frames_left));
    }
    else
    {
        //After
        frames_left = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
           (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame - 1;
       Logger::Instance()->Log(INFO, "Frames left until end of the attack: " + std::to_string(frames_left));
    }

    bool player_two_is_to_the_left = (m_state->m_memory->player_one_x > m_state->m_memory->player_two_x);
    //If we're in upsmash/jab range, then prepare for attack
    if(m_state->m_memory->player_two_facing == player_two_is_to_the_left && //Facing the right way?
        (distance < FOX_UPSMASH_RANGE ||
        (distance < FOX_UPSMASH_RANGE - 25.5 && (m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING))))
    {

        int frameDelay = 9; //Frames until the first smash hitbox, plus one for strage startup latency and another for charge lag
        if(m_state->m_memory->player_two_action == DASHING ||
            m_state->m_memory->player_two_action == RUNNING)
        {
            frameDelay += 4;
        }

        //Do we have time to upsmash? Do that.
        if(frames_left > frameDelay)
        {
            //Do two less frames of charging than we could, just to be safe
            CreateChain3(SmashAttack, SmashAttack::UP, std::max(0, frames_left - frameDelay));
            m_chain->PressButtons();
            return;
        }

        //Do we have time to jab? Do that.
        if(frames_left > 3 &&
            m_state->m_memory->player_two_action != DASHING &&
            m_state->m_memory->player_two_action != RUNNING)
        {
            CreateChain(Jab);
            m_chain->PressButtons();
            return;
        }
    }

    //Is it safe to wavedash in after shielding the attack?
    //  Don't wavedash off the edge of the stage
    if(frames_left > 15 &&
        m_state->m_memory->player_two_action == SHIELD_RELEASE &&
        (m_state->getStageEdgeGroundPosition() > std::abs(m_state->m_memory->player_two_x) + 10))
    {
        CreateChain2(Wavedash, player_two_is_to_the_left);
        m_chain->PressButtons();
        return;
    }

    //Default to walking in towards the player
    CreateChain2(Walk, player_two_is_to_the_left);
    m_chain->PressButtons();
    return;
}
