#include "Escape.h"
#include "../Chains/SmashDI.h"
#include "../Chains/Nothing.h"
#include "../Chains/Struggle.h"
#include "../Chains/DI.h"

Escape::Escape()
{
    m_chain = NULL;
}

Escape::~Escape()
{
    delete m_chain;
}

void Escape::DetermineChain()
{
    if(m_state->m_memory->player_two_action == TUMBLING)
    {
        CreateChain2(Struggle, true);
        m_chain->PressButtons();
        return;
    }

    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    //SmashDI
    if(m_state->isDamageState((ACTION)m_state->m_memory->player_two_action) &&
        m_state->m_memory->player_two_hitlag_frames_left > 1)
    {
        //Always SDI away and up
        bool isOnRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;
        CreateChain2(SmashDI, isOnRight);
        m_chain->PressButtons();
        return;
    }

    //Regular DI
    if(m_state->isDamageState((ACTION)m_state->m_memory->player_two_action))
    {
        double x=0, y=0;
        //TODO: More DI scenarios
        if(m_state->m_memory->player_two_action == THROWN_UP)
        {
            //Randomish choice between left and right
            x = m_state->m_memory->frame ? 0 : 1;
            y = .5;
        }
        else if(m_state->m_memory->player_two_action == THROWN_DOWN ||
            m_state->m_memory->player_two_action == THROWN_BACK)
        {
            //DI away
            x = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x ? 0 : 1;
            y = .5;
        }
        else if(m_state->m_memory->player_two_action == THROWN_FORWARD)
        {
            //DI away
            x = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x ? 1 : 0;
            y = .5;
        }
        else
        {
            //If we don't know what else to do, DI up
            x = .5;
            y = 1;
        }

        CreateChain3(DI, x, y);
        m_chain->PressButtons();
        return;
    }

    //Struggle out of grabs
    if(m_state->isGrabbedState((ACTION)m_state->m_memory->player_two_action))
    {
        CreateChain2(Struggle, false);
        m_chain->PressButtons();
        return;
    }

    //Do nothing fallback
    CreateChain(Nothing);
    m_chain->PressButtons();
}
