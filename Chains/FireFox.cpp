#include <cmath>
#include <math.h>

#include "FireFox.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"

void FireFox::PressButtons()
{
    //Firefox
    if(m_state->m_memory->player_two_action != FIREFOX_WAIT_AIR &&
      m_state->m_memory->player_two_action != FIREFOX_AIR)
    {
        if(!m_hasUpBd)
        {
            m_hasUpBd = true;
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, .5, 1);
            m_controller->pressButton(Controller::BUTTON_B);
            return;
        }
        else
        {
            m_hasUpBd = false;
            m_controller->emptyInput();
            return;
        }

    }

    if(m_state->m_memory->player_two_action == FIREFOX_WAIT_AIR)
    {
        if(!m_sweetspot)
        {
            m_controller->tiltAnalog(Controller::BUTTON_MAIN, m_isRightEdge ? 0 : 1, 1);
            return;
        }
        else
        {
            double stageEdgex = m_isRightEdge ? m_state->getStageEdgePosition() : (-1.0) * m_state->getStageEdgePosition();
            double diff_x = stageEdgex - m_state->m_memory->player_two_x;
            double diff_y = (EDGE_HANGING_Y_POSITION/2) - m_state->m_memory->player_two_y;
            double larger_magnitude = std::max(std::abs(diff_x), std::abs(diff_y));

            //Scale down values to between 0 and 1
            double x = diff_x / larger_magnitude;
            double y = diff_y / larger_magnitude;

            m_controller->tiltAnalog(Controller::BUTTON_MAIN, x, y);
            return;
        }
    }

    if(m_state->m_memory->player_two_action == FIREFOX_AIR)
    {
        m_controller->emptyInput();
        return;
    }
}

bool FireFox::IsInterruptible()
{
    if(m_state->m_memory->player_two_action != FIREFOX_WAIT_AIR &&
        m_state->m_memory->player_two_action != FIREFOX_AIR)
    {
        return true;
    }
    if(m_state->m_memory->frame - m_startingFrame > 100)
    {
        //Safety return. In case we screw something up, don't permanently get stuck in this chain.
        return true;
    }
    return false;
}

FireFox::FireFox(bool sweetspot)
{
    //Quick variable to tell us which edge we're on
    m_isRightEdge = m_state->m_memory->player_two_x > 0;
    m_startingFrame = m_state->m_memory->frame;
    m_hasUpBd = false;
    m_sweetspot = sweetspot;
    //If we're over the stage, override this
    if(std::abs(m_state->m_memory->player_two_x) < m_state->getStageEdgeGroundPosition())
    {
        m_sweetspot = false;
    }
}

FireFox::~FireFox()
{
}
