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
};

#endif
