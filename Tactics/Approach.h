#ifndef APPROACH_H
#define APPROACH_H

#include "Tactic.h"

//This tactic can be used to safely get in close with our opponent if they are not near
class Approach : public Tactic
{

public:

    Approach(bool);
    ~Approach();
    void DetermineChain();
    std::string ToString(){return "Approach";};
    bool IsInterruptible();

private:
    bool m_canInterrupt;
    uint m_frameStarted;
};

#endif
