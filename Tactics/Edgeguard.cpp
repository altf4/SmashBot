#include <cmath>
#include <math.h>

#include "Edgeguard.h"
#include "../Util/Constants.h"
#include "../Chains/Nothing.h"
#include "../Chains/JumpCanceledShine.h"
#include "../Chains/GrabEdge.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/DI.h"
#include "../Chains/MarthKiller.h"
#include "../Chains/Waveshine.h"
#include "../Chains/EdgeStall.h"
#include "../Chains/DashDance.h"
#include "../Util/Controller.h"
#include "../Util/Logger.h"

Edgeguard::Edgeguard()
{
    m_chain = NULL;
}

Edgeguard::~Edgeguard()
{
    delete m_chain;
}

void Edgeguard::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    double lowerEventHorizon = MARTH_LOWER_EVENT_HORIZON;
    if(m_state->m_memory->player_one_jumps_left == 0)
    {
        lowerEventHorizon += MARTH_DOUBLE_JUMP_HEIGHT;
    }

    //Marth is dead if he's at this point
    if(m_state->m_memory->player_one_y < lowerEventHorizon)
    {
        if(m_state->m_memory->player_two_action == EDGE_HANGING)
        {
            CreateChain2(EdgeAction, WAVEDASH_UP);
            m_chain->PressButtons();
            return;
        }
        if(m_state->m_memory->player_two_on_ground)
        {
            CreateChain(Nothing);
            m_chain->PressButtons();
            return;
        }
    }

    //Edgehog our opponent if they're UP-B'ing sweetspotted.
    //Grab the edge if we're still on the stage
    if(m_state->m_memory->player_one_action == UP_B &&
        m_state->m_memory->player_two_action == EDGE_HANGING)
    {
        //Is marth so low that he must grab the edge? If so, just roll up.
        if(m_state->m_memory->player_one_y < MARTH_RECOVER_HIGH_EVENT_HORIZON + MARTH_DOUBLE_JUMP_HEIGHT)
        {
            CreateChain3(EdgeAction, ROLL_UP, 2);
            m_chain->PressButtons();
            return;
        }
        //If not, he might land on the stage. So, just stand up and attack on the other end
        else
        {
            CreateChain2(EdgeAction, STAND_UP);
            m_chain->PressButtons();
            return;
        }
    }

    //distance formula
    double distance = pow(std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x), 2);
    distance += pow(std::abs(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y), 2);
    distance = sqrt(distance);

    double edge_distance_x = std::abs(std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition());
    double edge_distance_y = std::abs(m_state->m_memory->player_one_y - EDGE_HANGING_Y_POSITION);
    double edge_distance = sqrt(pow(edge_distance_x, 2) + pow(edge_distance_y, 2));

    //If we're able to shine p1 right now, let's do that
    if(std::abs(distance) < FOX_SHINE_RADIUS &&
        !m_state->m_memory->player_one_invulnerable &&
        m_state->m_memory->player_one_action != AIRDODGE &&
        m_state->m_memory->player_one_action != MARTH_COUNTER &&
        m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING)
    {
        //Are we in a state where we can shine?
        if(m_state->m_memory->player_two_action == FALLING ||
            m_state->m_memory->player_two_action == EDGE_HANGING)
        {
            CreateChain(JumpCanceledShine);
            m_chain->PressButtons();
            return;
        }
    }

    //Refresh invincibility if the enemy is getting close
    if(m_state->m_memory->player_two_action == EDGE_HANGING &&
        distance < (2 * MARTH_FSMASH_RANGE) &&
        edge_distance > 25)
    {
        //Don't edge stall if opponent can up-b to the edge quickly
        if(edge_distance_y > MARTH_UP_B_HEIGHT + 10 ||
            ((edge_distance_x > MARTH_UP_B_X_DISTANCE) && (std::abs(m_state->m_memory->player_one_x) > m_state->getStageEdgePosition())))
        {
            CreateChain(EdgeStall);
            m_chain->PressButtons();
            return;
        }
    }

    //Drop down and shine the enemy if they are below us and we have enough invincibility
    int invincibilityFramesLeft = 29 - (m_state->m_memory->frame - m_state->m_edgeInvincibilityStart);
    //TODO Test out this 8 unit lateral leeway
    if(std::abs(m_state->m_memory->player_two_x - m_state->m_memory->player_one_x) < 8 &&
        (invincibilityFramesLeft * FOX_FASTFALL_SPEED) < distance &&
        m_state->m_memory->player_two_y > m_state->m_memory->player_one_y &&
        m_state->m_memory->player_one_y > (-1)*(FOX_DOUBLE_JUMP_HEIGHT) &&
        m_state->m_memory->player_one_on_ground &&
        m_state->m_memory->player_two_on_ground)
    {
        CreateChain2(EdgeAction, FASTFALL);
        m_chain->PressButtons();
        return;
    }

    //Alternatively, we can shine when they are hanging on the edge
    if(std::abs(m_state->getStageEdgeGroundPosition() - std::abs(m_state->m_memory->player_two_x)) < 2 &&
        m_state->m_memory->player_one_action == EDGE_HANGING &&
        !m_state->m_memory->player_one_invulnerable)
    {
        CreateChain(Waveshine);
        m_chain->PressButtons();
        return;
    }

    //Dash dance around the edge
    if((m_state->m_memory->player_one_action == SLIDING_OFF_EDGE ||
        m_state->m_memory->player_one_action == EDGE_CATCHING ||
        m_state->m_memory->player_one_action == EDGE_HANGING) &&
        m_state->m_memory->player_two_on_ground)
    {
        bool onLeft = m_state->m_memory->player_one_x < 0;
        double pivotPoint = onLeft ? (-1) * m_state->getStageEdgeGroundPosition() : m_state->getStageEdgeGroundPosition();
        CreateChain3(DashDance, pivotPoint, 0);
        m_chain->PressButtons();
        return;
    }

    //If we're still on the stage, see if it's safe to grab the edge
    if(m_state->m_memory->player_two_on_ground)
    {
        //If the enemy is in a stunned damage state, go ahead and try.
        if(m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) &&
            m_state->m_memory->player_one_hitstun_frames_left > 15)
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }

        //Calculate distance between players
        double distance = pow(std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition(), 2);
        distance += pow(m_state->m_memory->player_one_y, 2);
        distance = sqrt(distance);

        //If marth is out of attack range and UP-B range, then go ahead and do it
        if(distance > MARTH_FSMASH_RANGE &&
            (std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition() > MARTH_UP_B_X_DISTANCE + 5 ||
            edge_distance_y > MARTH_UP_B_HEIGHT + 15))
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }

        //If marth is side-B'ing (out of attack range) then it's safe
        if(m_state->m_memory->player_one_action == SWORD_DANCE_1)
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }
    }

    //Do the marth killer if we're on the stage and Marth is going to be stuck recovering with an up-B
    if(m_state->m_memory->player_two_on_ground &&
        m_state->m_memory->player_one_jumps_left == 0 &&
        edge_distance_x > 30)
    {
        CreateChain(MarthKiller);
        m_chain->PressButtons();
        return;
    }

    if(m_state->m_memory->player_two_on_ground &&
        std::abs(m_state->m_memory->player_two_x) + .01 < m_state->getStageEdgePosition())
    {
        bool onLeft = m_state->m_memory->player_one_x < 0;
        double pivotPoint = onLeft ? (-1) * m_state->getStageEdgeGroundPosition() : m_state->getStageEdgeGroundPosition();
        CreateChain3(DashDance, pivotPoint, 0);
        m_chain->PressButtons();
        return;
    }

    //Aim at our opponent if we're falling at them
    if(m_state->m_memory->player_two_y > m_state->m_memory->player_one_y &&
        m_state->m_memory->player_two_action == FALLING)
    {
        CreateChain3(DI, m_state->m_memory->player_one_x > m_state->m_memory->player_two_x ? true : false, .5);
        m_chain->PressButtons();
        return;
    }

    //Just hang out and do nothing
    CreateChain(Nothing);
    m_chain->PressButtons();
    return;
}
