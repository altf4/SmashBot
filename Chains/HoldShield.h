#ifndef HOLD_SHIELD_H
#define HOLD_SHIELD_H

#include "Chain.h"

//Hold down on shield (as opposed to powershielding)
class HoldShield : public Chain
{

public:

    HoldShield(uint frames);
    ~HoldShield();
    //Determine what buttons to press in order to execute our tactic
    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "HoldShield";};

private:
    uint m_holdFrames;

};

#endif
