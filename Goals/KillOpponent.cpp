#include "KillOpponent.h"
#include "../Strategies/Bait.h"
#include "../Strategies/Sandbag.h"

#include <iostream>

KillOpponent::KillOpponent()
{
    m_strategy = NULL;
}

KillOpponent::~KillOpponent()
{
    delete m_strategy;
}

void KillOpponent::Strategize()
{
    //Melee is inconsistent and some actions are indexed from zero instead of one
    // This throws all our math off, so let's fix that problem
    if(m_state->isIndexedFromZero((ACTION)m_state->m_memory->player_one_action))
    {
        m_state->m_memory->player_one_action_frame++;
    }
    if(m_state->isIndexedFromZero((ACTION)m_state->m_memory->player_two_action))
    {
        m_state->m_memory->player_two_action_frame++;
    }

    //XXX: Uncomment this to test what frames actions are indexed from
    // if(m_state->m_memory->player_one_action_frame == 0)
    // {
    //     std::cout << std::hex << "Add it to the list: 0x" << m_state->m_memory->player_one_action << std::endl;
    // }
    // if(m_state->m_memory->player_two_action_frame == 0)
    // {
    //     std::cout << std::hex << "Add it to the list: 0x" << m_state->m_memory->player_two_action << std::endl;
    // }

    //If the opponent just started a roll, remember where they started from
    if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_action_frame <= 1)
    {
        m_state->m_rollStartPosition = m_state->m_memory->player_one_x;
        m_state->m_rollStartSpeed = m_state->m_memory->player_one_speed_x_attack;
        m_state->m_rollStartSpeedSelf = m_state->m_memory->player_one_speed_ground_x_self;
    }

    if(m_state->m_memory->player_one_action == EDGE_CATCHING &&
        m_state->m_memory->player_one_action_frame == 1)
    {
        m_state->m_edgeInvincibilityStart = m_state->m_memory->frame;
    }

    //If the opponent is invincible, don't attack them. Just dodge everything they do
    //UNLESS they are invincible due to rolling on the stage. Then go ahead and punish it, it will be safe by the time
    //  they are back up.
    if(m_state->m_memory->player_one_invulnerable &&
        m_state->m_memory->player_one_action != EDGE_GETUP_SLOW &&
        m_state->m_memory->player_one_action != EDGE_GETUP_QUICK &&
        m_state->m_memory->player_one_action != EDGE_ROLL_SLOW &&
        m_state->m_memory->player_one_action != EDGE_ROLL_QUICK)
    {
        CreateStrategy(Sandbag);
        m_strategy->DetermineTactic();
    }
    else
    {
        CreateStrategy(Bait);
        m_strategy->DetermineTactic();
    }

}
