#ifndef ESCAPE_H
#define ESCAPE_H
#include "Tactic.h"

class Escape : public Tactic
{

public:

    Escape();
    ~Escape();
    void DetermineChain();
    std::string ToString(){return "Escape";};
};

#endif
