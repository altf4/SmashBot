#ifndef CCATTACK_H
#define CCATTACK_H

#include "Chain.h"
#include "../Util/Controller.h"

class CrouchCancelAttack : public Chain
{

public:

    enum CC_ATTACK
    {
        CC_SHINE, CC_UPSMASH, CC_DOWNSMASH,
    };

    CrouchCancelAttack(CC_ATTACK d);
    ~CrouchCancelAttack();

    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "CrouchCancelAttack";};

private:
    CC_ATTACK m_attack;
    bool m_hasAttacked;
};

#endif
