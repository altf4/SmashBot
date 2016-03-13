#include <cmath>

#include "Walk.h"
void Walk::PressButtons()
{
    //Don't walk off the edge of the stage
    if(m_state->getStageEdgeGroundPosition() - std::abs(m_state->m_memory->player_two_x) < 5 &&
        (m_isRight == (m_state->m_memory->player_two_x > 0)))
    {
        m_controller->emptyInput();
        return;
    }

    switch(m_state->m_memory->player_two_action)
    {
        case WALK_SLOW:
        {
            if(m_isRight)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .683, .5);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .316, .5);
            }
            break;
        }
        case WALK_MIDDLE:
        {
            if(m_isRight)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .738, .5);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .261, .5);
            }
            break;
        }
        case WALK_FAST:
        {
            if(m_isRight)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, 1, .5);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, 0, .5);
            }
            break;
        }
        default:
        {
            if(m_isRight)
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .6, .5);
            }
            else
            {
                m_controller->tiltAnalog(Controller::BUTTON_MAIN, .4, .5);
            }
            break;
        }
    }
}

//We're always interruptible during a Walk
bool Walk::IsInterruptible()
{
    return true;
}

Walk::Walk(bool isRight)
{
    m_isRight = isRight;
}

Walk::~Walk()
{
}
