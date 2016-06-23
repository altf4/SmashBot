#include <cmath>
#include <math.h>

#include "Bait.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"
#include "../Tactics/ShowOff.h"

Bait::Bait()
{
    m_tactic = NULL;
    m_shieldedAttack = false;
    m_actionChanged = true;
    m_chargingLastFrame = false;
}

Bait::~Bait()
{
    delete m_tactic;
}

void Bait::DetermineTactic()
{
    CreateTactic(ShowOff);
    m_tactic->DetermineChain();
    return;
}
