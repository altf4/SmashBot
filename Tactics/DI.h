#ifndef DI_H
#define DI_H
#include "Tactic.h"

class DI : public Tactic
{

public:
    
    DI();
    ~DI();
    void DetermineChain();
    std::string ToString(){return "DI";};   

private:

    uint m_hitlagFramesLeftP1;
    uint m_hitlagFramesLeftP2;
    bool m_isFacingRightP1;
    bool m_isFacingRightP2;

};

#endif
