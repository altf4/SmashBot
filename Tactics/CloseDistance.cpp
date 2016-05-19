#include <cmath>

#include "CloseDistance.h"
#include "../Chains/Run.h"
#include "../Util/Constants.h"

CloseDistance::CloseDistance()
{
    m_chain = NULL;
}

CloseDistance::~CloseDistance()
{
    delete m_chain;
}

void CloseDistance::DetermineChain()
{
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

    //Default to charging at our opponent
    double pivotPoint = m_state->m_memory->player_one_x;

    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    //Do we have to stay away from their attack? Don't run right into an attack. Dash dance outside it until it's over
    if(distance < MARTH_FSMASH_RANGE * 1.1)
    {
        //Don't bother dodging if the attack is over
        if(m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character, (ACTION)m_state->m_memory->player_one_action) >=
            m_state->m_memory->player_one_action_frame)
        {
            //Don't bother dodging if the attack is in the wrong direction
            bool player_one_is_to_the_left = (m_state->m_memory->player_one_x - m_state->m_memory->player_two_x > 0);
            if((m_state->m_memory->player_one_facing != player_one_is_to_the_left || (m_state->isReverseHit((ACTION)m_state->m_memory->player_one_action))) &&
                (m_state->m_memory->player_two_on_ground ||
                m_state->m_memory->player_two_action == EDGE_HANGING ||
                m_state->m_memory->player_two_action == EDGE_CATCHING))
            {
                //Don't bother dodging if we're going to be invincible for the attack
                int invincibilityFramesLeft = 29 - (m_state->m_memory->frame - m_state->m_edgeInvincibilityStart);
                int framesUntilAttack = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
                    (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

                if(framesUntilAttack > invincibilityFramesLeft)
                {
                    if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
                    {
                        //Set the pivot point to be outside oppoent's attack range
                        bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
                        pivotPoint += onRight ? MARTH_FSMASH_RANGE * 1.2 : MARTH_FSMASH_RANGE * -1.2;
                    }
                }
            }
        }
    }

    //Run to the pivot point!

    //Make a new Run chain, since it's always interruptible
    delete m_chain;
    m_chain = NULL;
    bool left_of_pivot_position = m_state->m_memory->player_two_x < pivotPoint;
    CreateChain2(Run, left_of_pivot_position);
    m_chain->PressButtons();
    return;
}
