#include <cmath>

#include "ShowOff.h"
#include "../Chains/Multishine.h"

ShowOff::ShowOff()
{
    m_chain = NULL;
}

ShowOff::~ShowOff()
{
    delete m_chain;
}

void ShowOff::DetermineChain()
{
    CreateChain(Multishine);
    m_chain->PressButtons();
    return;
}
