#ifndef _LOGGER
#define _LOGGER

#include <string>

#include "../Goals/Goal.h"

enum LOG_LEVEL
{
    INFO,       //Logged to the NOTES section of the frame CSV log (does nothing if --debug not selected)
    WARNING,    //Output to stderr
    ERROR,      //Output to stderr in red
};

class Logger {
public:
    static Logger *Instance();

    //Log a string at a given log level
    void Log(LOG_LEVEL, std::string);

    //Write a frame's gamestate to the log along with any notes
    void LogFrame();

    //Get the raw string of the log
    std::string DumpLog();

    //Save the Goal pointer
    void SetGoal(Goal *goal);

    void SetDebug(bool);

private:
    Logger();
    static Logger *m_instance;

    bool m_isDebugMode;
    Goal *m_goal;
    std::string m_debuglog;
    std::string m_frameNote;
};

#endif
