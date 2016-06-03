#include <cmath>

#include "CloseDistance.h"
#include "../Chains/DashDance.h"
#include "../Util/Constants.h"

CloseDistance::CloseDistance(bool canInterrupt)
{
    m_canInterrupt = canInterrupt;
    m_chain = NULL;
    m_frameStarted = m_state->m_memory->frame;
}

CloseDistance::~CloseDistance()
{
    delete m_chain;
}

bool CloseDistance::IsInterruptible()
{
    if(!m_canInterrupt)
    {
        return false;
    }
    return m_chain->IsInterruptible();
}

void CloseDistance::DetermineChain()
{
    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    //We have finished approaching and can now be interrupted again
    if(distance < FOX_SHINE_RADIUS ||
        m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
    {
        m_canInterrupt = true;
    }
    if(m_state->m_memory->frame - m_frameStarted > 60)
    {
        //Safety escape to make sure we don't get stuck approaching somehow
        m_canInterrupt = true;
    }

    CreateChain3(DashDance, m_state->m_memory->player_one_x, 0);
    m_chain->PressButtons();
    return;
}
