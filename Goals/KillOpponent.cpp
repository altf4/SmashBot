#include "KillOpponent.h"
#include "../Strategies/Bait.h"
#include "../Strategies/Sandbag.h"

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
    //If the opponent just started a roll, remember where they started from
    if(m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_action_frame == 1)
    {
        m_state->m_rollStartPosition = m_state->m_memory->player_one_x;
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
