#ifndef BOARDPLATFORM_H
#define BOARDPLATFORM_H

#include "Chain.h"

//Board a given platform (typically by jumping onto it)
class BoardPlatform : public Chain
{

public:

    enum PLATFORM
    {
        LEFT_PLATFORM, RIGHT_PLATFORM, TOP_PLATFORM,
    };

    BoardPlatform(PLATFORM);
    ~BoardPlatform();
    //Determine what buttons to press in order to execute our tactic
    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "BoardPlatform";};

private:
    PLATFORM m_platform;
    double m_platform_left_edge;
    double m_platform_right_edge;
    double m_platform_height;
};

#endif
