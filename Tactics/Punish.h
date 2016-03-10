#ifndef PUNISH_H
#define PUNISH_H

#include "Tactic.h"

//Keep the opponent in the air
class Punish : public Tactic
{

public:
    Punish();
    ~Punish();
    void DetermineChain();
    std::string ToString(){return "Punish";};

private:
    double m_roll_position;
};

#endif
