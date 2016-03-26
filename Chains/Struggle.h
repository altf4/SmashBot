#ifndef STRUGGLE_H
#define STRUGGLE_H

#include "Chain.h"

class Struggle : public Chain
{

public:
    Struggle(bool);
    ~Struggle();
    bool IsInterruptible();
    void PressButtons();
    std::string ToString(){return "Struggle";};

private:
    bool m_isWiggle;
};

#endif
