#include <cmath>
#include <cstdlib>

#include "KeepDistance.h"
#include "../Chains/DashDance.h"
#include "../Chains/BoardPlatform.h"
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
    bool isLoopingAttack = m_state->m_memory->player_one_action == NEUTRAL_ATTACK_1 ||
        m_state->m_memory->player_one_action == NEUTRAL_ATTACK_2 ||
        m_state->m_memory->player_one_action == DOWNTILT;

    if(onRight)
    {
        pivotPoint += 1.1 * (isLoopingAttack ? MARTH_JAB_RANGE+2 : MARTH_FSMASH_RANGE);
    }
    else
    {
        pivotPoint -= 1.1 * (isLoopingAttack ? MARTH_JAB_RANGE+2 : MARTH_FSMASH_RANGE);
    }

    //Don't pivot past a given distance from the edge
    //  Or else we let the opponent corner us
    if(pivotPoint > m_state->getStageEdgeGroundPosition() - MARTH_FSMASH_RANGE)
    {
        pivotPoint = m_state->getStageEdgeGroundPosition() - MARTH_FSMASH_RANGE;
    }
    else if (pivotPoint < (-1) * (m_state->getStageEdgeGroundPosition() - MARTH_FSMASH_RANGE))
    {
        pivotPoint = (-1) * (m_state->getStageEdgeGroundPosition() - MARTH_FSMASH_RANGE);
    }

    //Is the opponent on a side platform and we're not?
    if((m_state->m_on_platform_left_opponent || m_state->m_on_platform_right_opponent) &&
        !m_state->m_on_platform_left_self &&
        !m_state->m_on_platform_right_self)
    {
        //Board the opposite platform they are on
        BoardPlatform::PLATFORM platform;
        if(m_state->m_on_platform_left_opponent)
        {
            platform = BoardPlatform::RIGHT_PLATFORM;
        }
        else
        {
            platform = BoardPlatform::LEFT_PLATFORM;
        }

        CreateChain2(BoardPlatform, platform);
        m_chain->PressButtons();
        return;
    }

    delete m_chain;
    m_chain = NULL;
    CreateChain3(DashDance, pivotPoint, 0);
    m_chain->PressButtons();
    return;
}
