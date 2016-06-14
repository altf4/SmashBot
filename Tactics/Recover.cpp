#include <typeinfo>
#include <math.h>
#include <cmath>

#include "Recover.h"
#include "../Util/Constants.h"
#include "../Chains/Nothing.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/FireFox.h"
#include "../Chains/FullJump.h"
#include "../Chains/DI.h"
#include "../Chains/Illusion.h"

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

    //If we're hanging on the egde, wavedash on
    if(m_state->m_memory->player_one_on_ground &&
        (m_state->m_memory->player_two_action == EDGE_HANGING ||
        m_state->m_memory->player_two_action == EDGE_CATCHING))
    {
        CreateChain2(EdgeAction, WAVEDASH_UP);
        m_chain->PressButtons();
        return;
    }

    //If we're off the stage...
    if(std::abs(m_state->m_memory->player_two_x) > m_state->getStageEdgeGroundPosition() + .001)
    {
        double xDistanceToEdge = std::abs(std::abs(m_state->m_memory->player_two_x) - m_state->getStageEdgePosition());
        bool onRight = m_state->m_memory->player_two_x > 0;
        bool acceptableFallState = m_state->m_memory->player_two_action == FALLING ||
            m_state->m_memory->player_two_action == FALLING_AERIAL ||
            m_state->m_memory->player_two_action == FALLING_AERIAL ||
            DOWN_B_AIR;

        //Can we just fall and grab the edge?
        if(acceptableFallState &&
            m_state->m_memory->player_one_action != EDGE_HANGING &&
            m_state->m_memory->player_one_action != EDGE_CATCHING &&
            xDistanceToEdge < 4.5 &&
            m_state->m_memory->player_two_y > -9)
        {
            if(m_state->m_memory->player_two_facing != onRight)
            {
                CreateChain(Nothing);
                m_chain->PressButtons();
                return;
            }
            else
            {
                if(m_state->m_memory->player_two_y < -6 &&
                  m_state->m_memory->player_two_action != FOX_ILLUSION)
                {
                    //Illusion
                    CreateChain2(Illusion, !onRight);
                    m_chain->PressButtons();
                    return;
                }
                else
                {
                    CreateChain(Nothing);
                    m_chain->PressButtons();
                    return;
                }
            }
        }

        if(m_state->m_memory->player_two_y < -4 &&
          m_state->m_memory->player_two_y > -8 &&
          m_state->m_memory->player_two_action != FOX_ILLUSION)
        {
            //Illusion
            CreateChain2(Illusion, !onRight);
            m_chain->PressButtons();
            return;
        }

        //Can we grab the edge, but are moving upwards?
        if(xDistanceToEdge < 4.5 &&
            m_state->m_memory->player_two_y > -10 &&
            m_state->m_memory->player_two_facing != onRight &&
            m_state->m_memory->player_two_speed_y_self > 0)
        {
            CreateChain(FireFox);
            m_chain->PressButtons();
            return;
        }

        //Do we still have a jump. If so, jump
        if(m_state->m_memory->player_two_jumps_left > 0)
        {
            CreateChain(FullJump);
            m_chain->PressButtons();
            return;
        }

        //If we're jumping, just keep jumping
        if((m_state->m_memory->player_two_action == JUMPING_ARIAL_FORWARD ||
          m_state->m_memory->player_two_action == JUMPING_ARIAL_BACKWARD) &&
          m_state->m_memory->player_two_speed_y_self > 0)
        {
            CreateChain3(DI, onRight ? 0 : 1, .5);
            m_chain->PressButtons();
            return;
        }
    }

    //Firefox back
    CreateChain(FireFox);
    m_chain->PressButtons();
    return;
}
