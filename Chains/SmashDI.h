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
    bool m_goRight;
    uint m_startingFrame;
    bool m_alternateDirection;
};

#endif
