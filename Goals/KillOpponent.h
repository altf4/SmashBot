#ifndef KILL_OPPONENT_H
#define KILL_OPPONENT_H

#include "Goal.h"
#include "../Util/GameState.h"

class KillOpponent : public Goal
{
public:
    KillOpponent();
    ~KillOpponent();
    //Determine what the best strategy is
    void Strategize();
    std::string ToString(){return "KillOpponent";};

private:
    //The action the opponent was in last frame
    ACTION m_lastAction;

    //The action frame of last action. Used for keeping track of wavedash slide frames
    uint m_lastActionFrame;
};

#endif
