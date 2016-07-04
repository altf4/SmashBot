#include <cmath>

#include "Approach.h"
#include "../Chains/DashDance.h"
#include "../Chains/Run.h"
#include "../Chains/BoardPlatform.h"
#include "../Util/Constants.h"

Approach::Approach(bool canInterrupt)
{
    m_canInterrupt = canInterrupt;
    m_chain = NULL;
    m_frameStarted = m_state->m_memory->frame;
}

Approach::~Approach()
{
    delete m_chain;
}

bool Approach::IsInterruptible()
{
    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
        distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
        distance = sqrt(distance);

    uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    bool beforeAttack = m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_action_frame < lastHitboxFrame;

    //We have finished approaching and can now be interrupted again
    if(distance < FOX_SHINE_RADIUS ||
        beforeAttack)
    {
        return true;
    }
    if(m_state->m_memory->frame - m_frameStarted > 120)
    {
        //Safety escape to make sure we don't get stuck approaching somehow
        return true;
    }

    if(m_state->m_memory->player_two_action == WAVEDASH_SLIDE)
    {
        return true;
    }

    if(!m_canInterrupt)
    {
        return false;
    }
    return m_chain->IsInterruptible();
}

void Approach::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    bool isLoopingAttack = m_state->m_memory->player_one_action == NEUTRAL_ATTACK_1 ||
        m_state->m_memory->player_one_action == NEUTRAL_ATTACK_2 ||
        m_state->m_memory->player_one_action == DOWNTILT;

    bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;

    if(isLoopingAttack)
    {
        CreateChain2(Run, onRight ? 0 : 1);
        m_chain->PressButtons();
        return;
    }

    CreateChain3(DashDance, m_state->m_memory->player_one_x, 0);
    m_chain->PressButtons();
    return;
}
