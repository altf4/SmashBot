#include <cmath>
#include <cstdlib>
#include <math.h>

#include "CrouchCancelAttack.h"
#include "../Util/Constants.h"

void CrouchCancelAttack::PressButtons()
{
    if(m_hasAttacked)
    {
        m_controller->emptyInput();
        return;
    }

    if(m_state->m_memory->player_two_action != CROUCHING &&
        m_state->m_memory->player_two_on_ground)
    {
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
        return;
    }

    //Calculate distance between players
    double distance = pow(std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition(), 2);
    distance += pow(m_state->m_memory->player_one_y, 2);
    distance = sqrt(distance);

    if(m_attack == CC_SHINE)
    {
        if(distance < FOX_SHINE_RADIUS &&
            m_state->m_memory->player_one_hitstun_frames_left == 0)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
            m_controller->pressButton(Controller::BUTTON_B);
            m_hasAttacked = true;
            return;
        }
    }
    if(m_attack == CC_UPSMASH)
    {
        if(distance < FOX_UPSMASH_RANGE_NEAR &&
            m_state->m_memory->player_one_hitstun_frames_left == 0)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
            m_controller->tiltAnalog(Controller::BUTTON_C, .5, 1);
            m_hasAttacked = true;
            return;
        }
    }
    //TODO: Actually figure out the downsmash range
    if(m_attack == CC_DOWNSMASH)
    {
        if(distance < FOX_UPSMASH_RANGE_NEAR &&
            m_state->m_memory->player_one_hitstun_frames_left == 0)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
            m_controller->tiltAnalog(Controller::BUTTON_C, .5, 0);
            m_hasAttacked = true;
            return;
        }
    }

    m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 0);
}

bool CrouchCancelAttack::IsInterruptible()
{
    //Safety return. In case we screw something up, don't permanently get stuck in this chain.
    if(m_state->m_memory->frame - m_startingFrame > 240)
    {
        return true;
    }

    //Don't return if we're still in the downsmash animation or starting a shine
    if(m_state->m_memory->player_two_action == DOWNSMASH ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND_START ||
        m_state->m_memory->player_two_action == DOWN_B_STUN)
    {
        return false;
    }


    return m_hasAttacked;
}

CrouchCancelAttack::CrouchCancelAttack(CC_ATTACK attack)
{
    m_attack = attack;
    m_hasAttacked = false;
}

CrouchCancelAttack::~CrouchCancelAttack()
{
}
