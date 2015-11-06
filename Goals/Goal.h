#ifndef GOAL_H
#define GOAL_H

#include "../Strategies/Strategy.h"

//The Goal of the AI represents the highest level objective. What is it trying to do? Win the match?
//  Embarras your opponent? Maybe it's not even supposed to play at all, and just show off tech skill,
//  like during handwarmers.
class Goal
{

public:
    virtual ~Goal() = 0;
    //TODO: Eventually, we're going to set other top level goals. Stuff like "sandbag" or "swag".
    //  For now, let's concentrate on winning the game

    //Determine what the best strategy is, based on the current matchup / config.
    //  Not a whole lot of decisions to be made at this point
    //TODO: Again, we're just handling the Fox v Marth on FD matchup. So this will always be "bait" for now
    virtual void Strategize() = 0;

protected:
    Strategy *m_strategy;
};

Goal::~Goal()
{

}

#endif
