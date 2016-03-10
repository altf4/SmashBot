#ifndef EDGEACTION_H
#define EDGEACTION_H

#include "Chain.h"
#include "../Util/Controller.h"

enum EDGEACTION
{
    STAND_UP,
    ROLL_UP,
    ATTACK_UP,
    WAVEDASH_UP,
    TOURNAMENT_WINNER,
};

//Perform an action to get up from the edge
class EdgeAction : public Chain
{

public:

    EdgeAction(EDGEACTION action, uint waitFrames = 0);
    ~EdgeAction();

    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "EdgeAction";};

private:
    EDGEACTION m_action;
    bool m_readyToInterrupt;
    uint m_waitFrames;
    bool m_onRight;
    bool m_pressedBack;
    bool m_pressedJump;
    bool m_pressedDodge;
};

#endif
