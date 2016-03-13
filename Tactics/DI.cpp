#include "DI.h"
#include "../Chains/SmashDI.h"
#include "../Chains/Nothing.h"

DI::DI()
{
    m_chain = NULL;
}

DI::~DI()
{
    delete m_chain;
}

void DI::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    //Start SDI Section
    if(m_state->m_memory->player_two_hitlag_frames_left > 1)
    {
        //Always SDI away and up
        bool isOnRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
        CreateChain2(SmashDI, isOnRight);
        m_chain->PressButtons();
        return;
    }
    //End SDI, Begin optimal DI section
    if(m_state->m_memory->player_two_hitlag_frames_left == 1)
    {
        //TODO: implement Trajectory DI
    }

    //Do nothing fallback
    CreateChain(Nothing);
    m_chain->PressButtons();
}
