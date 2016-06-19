#ifndef DASHDANCE_H
#define DASHDANCE_H

#include "Chain.h"

//Dash dance around a given axis and width
class DashDance : public Chain
{

public:

    DashDance(double, double);
    ~DashDance();
    //Determine what buttons to press in order to execute our tactic
    void PressButtons();
    bool IsInterruptible();
    std::string ToString(){return "DashDance";};

private:
    double m_pivotPoint;
    double m_radius;
    bool m_moonwalkPrevent;
};

#endif
