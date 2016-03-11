#ifndef SMASHDI_H
#define SMASHDI_H

#include "Chain.h"

class SmashDI : public Chain
{

public:
    SmashDI(bool facingRight);
    ~SmashDI();
    bool IsInterruptible();
    void PressButtons();
    std::string ToString(){return "SmashDI";};   

private:
    bool m_facingRight;
    uint m_startingFrame;
    
};

#endif
