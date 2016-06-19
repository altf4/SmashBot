#ifndef TECHCHASE_H
#define TECHCHASE_H

#include "Tactic.h"

class TechChase : public Tactic
{

public:
    TechChase();
    ~TechChase();
    void DetermineChain();
    std::string ToString(){return "TechChase";};

private:
    double m_endPosition;
    double m_pivotPosition;
};

#endif
