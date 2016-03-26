#ifndef STRUGGLE_H
#define STRUGGLE_H

#include "Chain.h"

class Struggle : public Chain
{

public:
    Struggle();
    ~Struggle();
    bool IsInterruptible();
    void PressButtons();
    std::string ToString(){return "Struggle";};
};

#endif
