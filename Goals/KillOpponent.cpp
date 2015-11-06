#include "KillOpponent.h"
#include "../Strategies/Bait.h"
#include "Goal.h"

KillOpponent::KillOpponent()
{
    //TODO: We're only supporting Bait for now. Eventually make this configurable
    m_strategy = new Bait();
}

KillOpponent::~KillOpponent()
{
    //TODO: We're only supporting Bait for now. Eventually make this configurable
    delete m_strategy;
}

void KillOpponent::Strategize()
{

}
