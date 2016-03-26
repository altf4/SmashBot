#ifndef DI_H
#define DI_H

#include "Chain.h"

class DI : public Chain
{

public:
    DI(double x, double y);
    ~DI();
    bool IsInterruptible();
    void PressButtons();
    std::string ToString(){return "DI";};

private:
    double m_x, m_y;
};

#endif
