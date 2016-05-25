#ifndef KEEP_DISTANCE_H
#define KEEP_DISTANCE_H

#include "Tactic.h"

//This tactic is used to maintain a safe distance away from our opponent where we can avoid attacks or rush in
class KeepDistance : public Tactic
{

public:

    KeepDistance();
    ~KeepDistance();
    void DetermineChain();
    std::string ToString(){return "KeepDistance";};

};

#endif
