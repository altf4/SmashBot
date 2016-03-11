#include <cstddef>
#include <sys/types.h>  // mkfifo
#include <sys/stat.h>   // mkfifo
#include <fcntl.h>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <pwd.h>

#include "Logger.h"
#include "GameState.h"

Logger* Logger::m_instance = NULL;

Logger *Logger::Instance()
{
    if (!m_instance)
    {
        m_instance = new Logger();
    }
    return m_instance;
}

Logger::Logger()
{
    //CSV header
    m_debuglog = "Frame,Goal,Strategy,Tactic,Chain,Player 1 x,Player 1 y,Player 2 x,Player 2 y,Player 1 Action,Player 2 Action,Player 1 Action Frame,Player 2 Action Frame," \
        "Player 1 Jumps Left,Player 2 Jumps Left,Player 1 Stock,Player 2 Stock,Player 1 Percent,Player 2 Percent";
    //Just to make sure Notes stays at the end
    m_debuglog += ",Notes";
    m_debuglog += "\n";
    m_isDebugMode = false;
}

void Logger::Log(LOG_LEVEL level, std::string log_string)
{
    switch(level)
    {
        case INFO:
        {
            if(!m_isDebugMode)
            {
                return;
            }
            if(m_frameNote != "")
            {
                m_frameNote += "\n";
            }
            m_frameNote += "INFO: " + log_string;
            break;
        }
        case WARNING:
        {
            std::cout << "WARNING: " << log_string << std::endl;
            break;
        }
        case ERROR:
        {
            std::cout << "ERROR: " << log_string << std::endl;
            break;
        }
    }
}

void Logger::LogFrame()
{

    if(!m_isDebugMode)
    {
        return;
    }

    GameState *state = GameState::Instance();

    //Frame
    m_debuglog += std::to_string(state->m_memory->frame);
    m_debuglog += ",";

    //Objectives
    if(m_goal == NULL)
    {
        m_debuglog += "NULL,NULL,NULL,NULL,";
    }
    else
    {
        m_debuglog += m_goal->ToStringCascade();
        m_debuglog += ",";
    }

    //Positions
    m_debuglog += std::to_string(state->m_memory->player_one_x);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_one_y);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_x);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_y);
    m_debuglog += ",";

    //Action states
    m_debuglog += std::to_string(state->m_memory->player_one_action);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_action);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_one_action_frame);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_action_frame);
    m_debuglog += ",";

    //Jumps
    m_debuglog += std::to_string(state->m_memory->player_one_jumps_left);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_jumps_left);
    m_debuglog += ",";

    //Stock and percentage
    m_debuglog += std::to_string(state->m_memory->player_one_stock);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_stock);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_one_percent);
    m_debuglog += ",";
    m_debuglog += std::to_string(state->m_memory->player_two_percent);
    m_debuglog += ",";

    //Notes
    m_debuglog += "\"" + m_frameNote + "\"";

    m_debuglog += "\n";
    m_frameNote = "";
}

std::string Logger::DumpLog()
{
    return m_debuglog;
}

void Logger::SetGoal(Goal *goal)
{
    m_goal = goal;
}

void Logger::SetDebug(bool isDebugMode)
{
    m_isDebugMode = isDebugMode;
}
