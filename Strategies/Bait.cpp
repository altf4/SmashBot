#include "Bait.h"
#include "../Tactics/CloseDistance.h"
#include "Strategy.h"

Bait::Bait()
{
    //TODO support more than just CloseDistance
    m_tactic = new CloseDistance();
}

Bait::~Bait()
{
    delete m_tactic;
}

void Bait::DetermineTactic()
{

}
