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

    //random number between 0 and 5
    double radius = rand() % 3;

    //Make a new radius every turn, so as to mix up the dash dance
    if(m_state->m_memory->player_two_action == TURNING)
    {
        delete m_chain;
        m_chain = NULL;
        radius = (rand() % 5);
    }

    CreateChain3(DashDance, pivotPoint, radius);
    m_chain->PressButtons();
    return;
}
