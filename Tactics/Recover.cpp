#include <typeinfo>
#include <math.h>
#include <cmath>

#include "Recover.h"
#include "../Util/Constants.h"
#include "../Chains/Nothing.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/FireFox.h"

Recover::Recover()
{
    m_chain = NULL;
}

Recover::~Recover()
{
    delete m_chain;
}

void Recover::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    //If we're hanging on the egde, do an edge stall
    if(m_state->m_memory->player_two_action == EDGE_HANGING ||
      m_state->m_memory->player_two_action == EDGE_CATCHING)
    {
        CreateChain2(EdgeAction, WAVEDASH_UP);
        m_chain->PressButtons();
        return;
    }

    //TODO: This is only rudimentary recovery. Needs to be expanded
    //If we're off the stage...
    if(std::abs(m_state->m_memory->player_two_x) > m_state->getStageEdgeGroundPosition() + .001)
    {
        if(m_state->m_memory->player_two_y > 0 &&
          m_state->m_memory->player_two_y < 10)
        {
            //Side-B back to the stage
        }
        else
        {
            //Firefox back
            CreateChain(FireFox);
            m_chain->PressButtons();
            return;
        }

    }

    //Default to nothing in towards the player
    CreateChain(Nothing);
    m_chain->PressButtons();
    return;
}
