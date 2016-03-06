#include "EdgeAction.h"

void EdgeAction::PressButtons()
{
    if(m_waitFrames > 0)
    {
        m_waitFrames--;
        m_controller->emptyInput();
        m_readyToInterrupt = false;
        return;
    }

    //Wait until we're not edge catching anymore
    if(m_state->m_memory->player_two_action == EDGE_CATCHING)
    {
        m_controller->emptyInput();
        return;
    }

    switch(m_action)
    {
        case STAND_UP:
        {
            if(m_state->m_memory->player_two_action == EDGE_HANGING)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .70);
                return;
            }
            break;
        }
        case ROLL_UP:
        {
            if(m_state->m_memory->player_two_action == EDGE_HANGING)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
                m_controller->pressButton(Controller::BUTTON_L);
                return;
            }
            break;
        }
        case ATTACK_UP:
        {
            if(m_state->m_memory->player_two_action == EDGE_HANGING)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, .5);
                m_controller->pressButton(Controller::BUTTON_A);
                return;
            }
            break;
        }
        case WAVEDASH_UP:
        {
            //If we're hanging on the edge, let go
            if(m_state->m_memory->player_two_action == EDGE_HANGING)
            {
                if(m_pressedBack)
                {
                    m_controller->emptyInput();
                    m_pressedBack = false;
                    break;
                }
                m_pressedBack = true;
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_onRight ? 1 : 0, .5);
                return;
            }
            //If we're falling, jump
            if(m_state->m_memory->player_two_action == FALLING)
            {
                if(m_pressedJump)
                {
                    m_controller->emptyInput();
                    m_pressedJump = false;
                    break;
                }
                m_pressedJump = true;
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_onRight ? 0 : 1, .5);
                m_controller->pressButton(Controller::BUTTON_Y);
                return;
            }
            //If we're above the stage, then wavedash into it
            if(m_state->m_memory->player_two_on_ground == false && m_state->m_memory->player_two_y > 0)
            {
                if(m_pressedDodge)
                {
                    m_controller->emptyInput();
                    m_pressedDodge = false;
                    break;
                }
                m_pressedDodge = true;
                m_controller->releaseButton(Controller::BUTTON_Y);
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_onRight ? 0 : 1, 0);
                m_controller->pressButton(Controller::BUTTON_L);
                return;
            }
            break;
        }
        case TOURNAMENT_WINNER:
        {
            //TODO
            break;
        }
    }

    //Reset the controller afterward
    m_controller->emptyInput();

    if(m_state->m_memory->player_two_action == STANDING ||
        m_state->m_memory->player_two_action == LANDING_SPECIAL)
    {
        m_readyToInterrupt = true;
    }
}

bool EdgeAction::IsInterruptible()
{
    return m_readyToInterrupt;
}

EdgeAction::EdgeAction(EDGEACTION action, uint waitFrames)
{
    m_action = action;
    m_readyToInterrupt = false;
    m_waitFrames = waitFrames;
    m_onRight = m_state->m_memory->player_two_x > 0;
    m_pressedBack = false;
    m_pressedJump = false;
    m_pressedDodge = false;
}

EdgeAction::~EdgeAction()
{
}
