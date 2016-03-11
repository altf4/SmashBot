#include "DI.h"
#include "../Chains/SmashDI.h"

DI::DI()
{
    m_chain = NULL;
    m_isFacingRightP1 = m_state->m_memory->player_one_facing;
    m_isFacingRightP2 = m_state->m_memory->player_two_facing;
    m_hitlagFramesLeftP1 = m_state->m_memory->player_one_hitlag_frames_left;
    m_hitlagFramesLeftP2 = m_state->m_memory->player_two_hitlag_frames_left;
}

DI::~DI()
{
    delete m_chain;
}

void DI::DetermineChain()
{   
    //Start SDI Section
    if(m_hitlagFramesLeftP2 > 1)
    {
        CreateChain2(SmashDI, m_isFacingRightP1);
        m_chain->PressButtons();
    }
    //End SDI, Begin optimal DI section
    if(m_hitlagFramesLeftP2 == 1)
    {
        //TODO: implement Trajectory DI
    }
}
