#include <cmath>
#include <cstdlib>
#include <math.h>

#include "BoardPlatform.h"
#include "../Util/Constants.h"
#include "../Util/Controller.h"

BoardPlatform::BoardPlatform(PLATFORM platform)
{
    m_platform = platform;

    m_platform_left_edge = 0;
    m_platform_right_edge = 0;
    m_platform_height = 0;

    if(m_platform == LEFT_PLATFORM)
    {
        m_platform_left_edge = (-1.0)*m_state->sidePlatformOutterEdge();
        m_platform_right_edge = (-1.0)*m_state->sidePlatformInnerEdge();
        m_platform_height = m_state->sidePlatformHeight();
    }
    if(m_platform == RIGHT_PLATFORM)
    {
        m_platform_left_edge = m_state->sidePlatformInnerEdge();
        m_platform_right_edge = m_state->sidePlatformOutterEdge();
        m_platform_height = m_state->sidePlatformHeight();
    }
    if(m_platform == TOP_PLATFORM)
    {
        m_platform_left_edge = m_state->topPlatformLeftEdge();
        m_platform_right_edge = m_state->topPlatformRightEdge();
        m_platform_height = m_state->topPlatformHeight();
    }
}

BoardPlatform::~BoardPlatform()
{
}

bool BoardPlatform::IsInterruptible()
{
    if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
    {
        return true;
    }

    //If we're on the platform, quit out
    if(m_state->m_memory->player_two_x > m_platform_left_edge &&
        m_state->m_memory->player_two_x < m_platform_right_edge &&
        m_state->m_memory->player_two_y + 1 > m_platform_height &&
        m_state->m_memory->player_two_on_ground)
    {
        return true;
    }

    //Safety return. In case we screw something up, don't permanently get stuck in this chain.
    if(m_state->m_memory->frame - m_startingFrame > 360)
    {
        return true;
    }
    return false;
}

void BoardPlatform::PressButtons()
{
    if(m_state->m_memory->player_two_action == DOWN_B_STUN)
    {
        m_controller->emptyInput();
        return;
    }

    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);
    //If we're able to shine p1 right now, let's do that
    if(std::abs(distance) < FOX_SHINE_RADIUS)
    {
        //Is the opponent in a state where they can get hit by shine?
        //And are we in a state where we can perform a shine?
        if(m_state->m_memory->player_one_action != SHIELD &&
            m_state->m_memory->player_one_action != SHIELD_REFLECT &&
            m_state->m_memory->player_one_action != SHIELD_START &&
            m_state->m_memory->player_one_action != SHIELD_STUN &&
            m_state->m_memory->player_one_action != MARTH_COUNTER &&
            m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING &&
            m_state->m_memory->player_one_action != EDGE_CATCHING &&
            m_state->m_memory->player_one_action != SPOTDODGE &&
            m_state->m_memory->player_one_action != GROUND_ATTACK_UP && //Can't punish before the attack on a getup attack
            m_state->m_memory->player_two_action != SHINE_TURN &&
            m_state->m_memory->player_two_action != DOWN_B_AIR &&
            m_state->m_memory->player_two_action != DOWN_B_STUN &&
            m_state->m_memory->player_two_jumps_left > 0)
        {
            //Shine
            m_controller->pressButton(Controller::BUTTON_B);
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0.5, 0);
            return;
        }
    }

    //If we're falling above the platform and in shine, hold shine
    if(m_state->m_memory->player_two_x > m_platform_left_edge &&
        m_state->m_memory->player_two_x < m_platform_right_edge &&
        m_state->m_memory->player_two_speed_y_self <= 0 &&
        m_state->m_memory->player_two_y > m_platform_height &&
        m_state->m_memory->player_two_action == DOWN_B_AIR)
    {
        //Hold Shine
        m_controller->pressButton(Controller::BUTTON_B);
        m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0.5, 0);
        return;
    }

    double platform_middle = (m_platform_right_edge + m_platform_left_edge) / 2.0;
    bool rightOfMiddle = m_state->m_memory->player_two_x > platform_middle;

    //Are we above the platform and rising?
    //TODO: apparently sometimes you don't need to be strictly above the platform. You can be a little below and that's fine
    //It depends on what frame of the jumping animation we're in
    if(m_state->m_memory->player_two_x > m_platform_left_edge &&
        m_state->m_memory->player_two_x < m_platform_right_edge &&
        m_state->m_memory->player_two_speed_y_self >= 0)
    {
        if(m_state->m_memory->player_two_y > m_platform_height)
        {
            //Air dodge downward towards the platform (towards the middle of the platform)
            if(std::abs(platform_middle - m_state->m_memory->player_two_x) < 5)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0.5, 0);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, rightOfMiddle ? 0.2 : 0.8, 0);
            }
            m_controller->pressButton(Controller::BUTTON_L);
            return;
        }
    }

    //Are we right underneath the platform?
    if(m_state->m_memory->player_two_x > m_platform_left_edge &&
        m_state->m_memory->player_two_x < m_platform_right_edge &&
        m_state->m_memory->player_two_y < m_platform_height)
    {
        //Jump
        if(m_state->m_memory->player_two_x > m_platform_left_edge + 5 &&
            m_state->m_memory->player_two_x < m_platform_right_edge - 5 &&
            (m_state->m_memory->player_two_action == TURNING ||
            m_state->m_memory->player_two_action == KNEE_BEND ||
            m_state->m_memory->player_two_action == STANDING))
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, rightOfMiddle ? 0 : 1, 0.5);
            m_controller->pressButton(Controller::BUTTON_Y);
            return;
        }

        //Double jump if we need to
        if(m_state->m_memory->player_two_speed_y_self <= 0 &&
            m_state->m_memory->player_two_jumps_left > 0)
        {
            m_controller->pressButton(Controller::BUTTON_Y);
            return;
        }

        //If we're jumping, keep jumping and move in towards the opponent
        if(m_state->m_memory->player_two_action == JUMPING_FORWARD ||
            m_state->m_memory->player_two_action == JUMPING_BACKWARD)
        {
            m_controller->releaseButton(Controller::BUTTON_Y);
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, rightOfMiddle ? 0 : 1, 0.5);
            return;
        }

        //Should we turn around? With a little room to spare, don't cut it too close
        if(m_state->m_memory->player_two_x > m_platform_left_edge + 5 &&
            m_state->m_memory->player_two_x < m_platform_right_edge - 5 &&
            m_state->m_memory->player_two_action == DASHING)
        {
            //Do a turn to kill our momentum
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_state->m_memory->player_two_facing ? 0 : 1, 0.5);
            return;
        }
    }

    //If we're not on the correct platform, dash under the correct one
    if(m_state->m_memory->player_two_on_ground &&
        m_state->m_memory->player_two_y + 1 < m_platform_height)
    {
        //If we're starting the turn around animation, keep pressing that way or else we'll get stuck in the slow turnaround
        if(m_state->m_memory->player_two_action == TURNING &&
            m_state->m_memory->player_two_action_frame == 1)
        {
            return;
        }

        //Dash back, since we're about to start running
        if(m_state->m_memory->player_two_action == DASHING &&
            m_state->m_memory->player_two_action_frame >= FOX_DASH_FRAMES-1)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, !m_state->m_memory->player_two_facing, .5);
            return;
        }

        //which direction should we dash at?
        if(m_state->m_memory->player_two_x < m_platform_left_edge)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 1, 0.5);
            return;
        }
        if(m_state->m_memory->player_two_x > m_platform_right_edge)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, 0.5);
            return;
        }
    }

    m_controller->emptyInput();
}
