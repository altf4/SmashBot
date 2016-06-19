#ifndef SANDBAG_H
#define SANDBAG_H

#include "Strategy.h"

//Be defensive and don't let our opponent hit us
class Sandbag : public Strategy
{

public:

    Sandbag();
    ~Sandbag();

    //Determine what tactic to employ in order to further our strategy
    void DetermineTactic();
    std::string ToString(){return "Sandbag";};

private:
    //Did the enemy's action change from last frame?
    bool m_actionChanged;
    //Have we shielded the opponent's current attack?
    bool m_shieldedAttack;
    //Was the opponent charging a smash last frame?
    bool m_chargingLastFrame;

};

#endif
