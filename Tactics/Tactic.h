#ifndef TACTIC_H
#define TACTIC_H

#include "../Chains/Chain.h"

//The tactic is a short term actionable objective
class Tactic
{

public:

    virtual ~Tactic() = 0;

    //Determine what tactic to employ in order to further our strategy, based on game state
    virtual void DetermineChain() = 0;

protected:
    Chain *m_chain;
};

Tactic::~Tactic()
{

}

#endif
