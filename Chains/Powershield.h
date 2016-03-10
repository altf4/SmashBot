#ifndef POWERSHIELD_H
#define POWERSHIELD_H

#include "Chain.h"

//Powershield an incoming attack
class Powershield : public Chain
{

public:

    Powershield();
    ~Powershield();
    //Determine what buttons to press in order to execute our tactic
    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "Powershield";};

private:
    uint m_letGo;
    uint m_frameShielded;
    bool m_isReverseFacing;
    bool m_hasShielded;
    bool m_endEarly;
};

#endif
