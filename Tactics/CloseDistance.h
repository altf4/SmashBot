#ifndef CLOSE_DISTANCE_H
#define CLOSE_DISTANCE_H

#include "Tactic.h"

//This tactic can be used to safely get in close with our opponent if they are not near
class CloseDistance : public Tactic
{

public:

    CloseDistance(bool);
    ~CloseDistance();
    void DetermineChain();
    std::string ToString(){return "CloseDistance";};
    bool IsInterruptible();

private:
    bool m_canInterrupt;
    uint m_frameStarted;
};

#endif
