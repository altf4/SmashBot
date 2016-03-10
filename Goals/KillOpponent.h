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

};

#endif
