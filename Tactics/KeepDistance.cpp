#include <cmath>

#include "KeepDistance.h"
#include "../Chains/DashDance.h"
#include "../Util/Constants.h"

KeepDistance::KeepDistance()
{
    m_chain = NULL;
}

KeepDistance::~KeepDistance()
{
    delete m_chain;
}

void KeepDistance::DetermineChain()
{
    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
    double pivotPoint = m_state->m_memory->player_one_x;
    if(onRight)
    {
        pivotPoint += 1.1 * MARTH_FSMASH_RANGE;
    }
    else
    {
        pivotPoint -= 1.1 * MARTH_FSMASH_RANGE;
    }

    delete m_chain;
    m_chain = NULL;
    CreateChain3(DashDance, pivotPoint, 0);
    m_chain->PressButtons();
    return;
}
