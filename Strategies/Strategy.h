#ifndef STRATEGY_H
#define STRATEGY_H
#include <typeinfo>
#include <string>

#include "../Tactics/Tactic.h"
#include "../Util/GameState.h"

//The strategy is a high level way of accomplishing the top level goal. You might call it a "playstyle"
//  or "gameplan".
class Strategy
{

public:
    Strategy(){m_state = GameState::Instance();};
    virtual ~Strategy(){};
    //Determine what tactic to employ in order to further our strategy
    // This decision is made on the basis of the game state
    virtual void DetermineTactic() = 0;

    virtual std::string ToString() = 0;

    std::string ToStringCascade(){return this->ToString() + "," + m_tactic->ToStringCascade();};

protected:

    //Returns if the given state allows us to perform any action
    bool ReadyForAction(uint a)
    {
        switch(a)
        {
            case STANDING:
                return true;
            case WALK_SLOW:
                return true;
            case WALK_MIDDLE:
                return true;
            case WALK_FAST:
                return true;
            case KNEE_BEND:
                return true;
            case CROUCHING:
                return true;
            case EDGE_TEETERING:
                return true;
            default:
                return false;
        }
        return false;
    }

    Tactic *m_tactic;
    GameState *m_state;
};

#define CreateTactic(TYPE) if(m_tactic==NULL){m_tactic = new TYPE();};if(typeid(*m_tactic) \
!= typeid(TYPE)){delete m_tactic;m_tactic = new TYPE();}
#define CreateTactic2(TYPE, ARG) if(m_tactic==NULL){m_tactic = new TYPE(ARG);};if(typeid(*m_tactic) \
!= typeid(TYPE)){delete m_tactic;m_tactic = new TYPE(ARG);}

#endif
