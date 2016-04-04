#ifndef GRABNTHROW_H
#define GRABNTHROW_H

#include "Chain.h"
#include "../Util/Controller.h"

enum THROW_DIRECTION
{
    UP_THROW,
    DOWN_THROW,
    BACK_THROW,
    FORWARD_THROW,
};

class GrabAndThrow : public Chain
{

public:

    GrabAndThrow(THROW_DIRECTION direction);
    ~GrabAndThrow();

    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "GrabAndThrow";};

private:
    THROW_DIRECTION m_direction;
};

#endif
