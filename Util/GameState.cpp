#include <string>
#include <algorithm>

#include "GameState.h"
#include "Constants.h"

GameState* GameState::m_instance = NULL;

GameState *GameState::Instance()
{
    if (!m_instance)
    {
        m_instance = new GameState();
    }
    return m_instance;
}

GameState::GameState()
{
    m_memory = new GameMemory();
    m_rollStartPosition = 0;
    m_edgeInvincibilityStart = 0;
    m_rollStartSpeed = 0;
    m_rollStartSpeedSelf = 0;
}

double GameState::getStageEdgePosition()
{
    double edge_position = 100;
    switch(m_memory->stage)
    {
        case BATTLEFIELD:
        {
            edge_position = 71.3078536987;
            break;
        }
        case FINAL_DESTINATION:
        {
            edge_position = 88.4735488892;
            break;
        }
        case DREAMLAND:
        {
            edge_position = 80.1791534424;
            break;
        }
        case FOUNTAIN_OF_DREAMS:
        {
            edge_position = 66.2554016113;
            break;
        }
    }
    return edge_position;
}

double GameState::getStageEdgeGroundPosition()
{
    double edge_position = 100;
    switch(m_memory->stage)
    {
        case BATTLEFIELD:
        {
            edge_position = 68.4000015259;
            break;
        }
        case FINAL_DESTINATION:
        {
            edge_position = 85.5656967163;
            break;
        }
        case DREAMLAND:
        {
            edge_position = 77.2713012695;
            break;
        }
        case FOUNTAIN_OF_DREAMS:
        {
            edge_position = 63.3475494385;
            break;
        }
    }
    return edge_position;
}

bool GameState::isDamageState(ACTION action)
{
    //Luckily, most of the damage states are contiguous
    if(action >= DAMAGE_HIGH_1 && action <= DAMAGE_FLY_ROLL)
    {
        return true;
    }
    if(action == THROWN_FORWARD ||
        action == THROWN_BACK ||
        action == THROWN_UP ||
        action == THROWN_DOWN ||
        action == DAMAGE_GROUND)
    {
        return true;
    }

    return false;
}

uint GameState::firstHitboxFrame(CHARACTER character, ACTION action)
{
    switch(character)
    {
        case MARTH:
        {
            switch(action)
            {
                case FSMASH_MID:
                {
                    return 10;
                }
                case DOWNSMASH:
                {
                    return 6;
                }
                case UPSMASH:
                {
                    return 13;
                }
                case DASH_ATTACK:
                {
                    return 12;
                }
                case GRAB:
                {
                    return 7;
                }
                case GRAB_RUNNING:
                {
                    return 10;
                }
                case FTILT_HIGH:
                case FTILT_HIGH_MID:
                case FTILT_MID:
                case FTILT_LOW_MID:
                case FTILT_LOW:
                {
                    return 7;
                }
                case UPTILT:
                {
                    return 7;
                }
                case DOWNTILT:
                {
                    return 7;
                }
                case SWORD_DANCE_1:
                case SWORD_DANCE_1_AIR:
                {
                    return 6;
                }
                case SWORD_DANCE_2_HIGH:
                case SWORD_DANCE_2_HIGH_AIR:
                {
                    return 12;
                }
                case SWORD_DANCE_2_MID:
                case SWORD_DANCE_2_MID_AIR:
                {
                    return 14;
                }
                case SWORD_DANCE_3_HIGH:
                case SWORD_DANCE_3_HIGH_AIR:
                {
                    return 13;
                }
                case SWORD_DANCE_3_MID:
                case SWORD_DANCE_3_MID_AIR:
                {
                    return 11;
                }
                case SWORD_DANCE_3_LOW:
                case SWORD_DANCE_3_LOW_AIR:
                {
                    return 15;
                }
                case SWORD_DANCE_4_HIGH:
                case SWORD_DANCE_4_HIGH_AIR:
                {
                    return 20;
                }
                case SWORD_DANCE_4_MID:
                case SWORD_DANCE_4_MID_AIR:
                {
                    return 23;
                }
                case SWORD_DANCE_4_LOW:
                case SWORD_DANCE_4_LOW_AIR:
                {
                    return 13;
                }
                case UP_B:
                case UP_B_GROUND:
                {
                    return 5;
                }
                case NAIR:
                {
                    return 6;
                }
                case UAIR:
                {
                    return 5;
                }
                case DAIR:
                {
                    return 6;
                }
                case BAIR:
                {
                    return 7;
                }
                case FAIR:
                {
                    return 4;
                }
                case NEUTRAL_ATTACK_1:
                {
                    return 4;
                }
                case NEUTRAL_ATTACK_2:
                {
                    return 6;
                }
                case NEUTRAL_B_ATTACKING:
                case NEUTRAL_B_ATTACKING_AIR:
                {
                    return 16;
                }
                case EDGE_ATTACK_SLOW:
                {
                    return 38;
                }
                case EDGE_ATTACK_QUICK:
                {
                    return 25;
                }
                case GROUND_ATTACK_UP:
                {
                    return 20;
                }
                default:
                {
                    return 0;
                    break;
                }
            }
            break;
        }
        default:
        {
            return 0;
            break;
        }
    }
}

uint GameState::lastHitboxFrame(CHARACTER character, ACTION action)
{
    switch(character)
    {
        case MARTH:
        {
            switch(action)
            {
                case FSMASH_MID:
                {
                    return 13;
                }
                case DOWNSMASH:
                {
                    return 23;
                }
                case UPSMASH:
                {
                    return 16;
                }
                case DASH_ATTACK:
                {
                    return 15;
                }
                case GRAB:
                {
                    return 8;
                }
                case GRAB_RUNNING:
                {
                    return 11;
                }
                case FTILT_HIGH:
                case FTILT_HIGH_MID:
                case FTILT_MID:
                case FTILT_LOW_MID:
                case FTILT_LOW:
                {
                    return 10;
                }
                case UPTILT:
                {
                    return 13;
                }
                case DOWNTILT:
                {
                    return 9;
                }
                case SWORD_DANCE_1:
                case SWORD_DANCE_1_AIR:
                {
                    return 8;
                }
                case SWORD_DANCE_2_HIGH:
                case SWORD_DANCE_2_HIGH_AIR:
                {
                    return 15;
                }
                case SWORD_DANCE_2_MID:
                case SWORD_DANCE_2_MID_AIR:
                {
                    return 16;
                }
                case SWORD_DANCE_3_HIGH:
                case SWORD_DANCE_3_HIGH_AIR:
                {
                    return 17;
                }
                case SWORD_DANCE_3_MID:
                case SWORD_DANCE_3_MID_AIR:
                {
                    return 14;
                }
                case SWORD_DANCE_3_LOW:
                case SWORD_DANCE_3_LOW_AIR:
                {
                    return 18;
                }
                case SWORD_DANCE_4_HIGH:
                case SWORD_DANCE_4_HIGH_AIR:
                {
                    return 25;
                }
                case SWORD_DANCE_4_MID:
                case SWORD_DANCE_4_MID_AIR:
                {
                    return 26;
                }
                case SWORD_DANCE_4_LOW:
                case SWORD_DANCE_4_LOW_AIR:
                {
                    return 38;
                }
                case UP_B:
                case UP_B_GROUND:
                {
                    return 10;
                }
                case NAIR:
                {
                    return 21;
                }
                case UAIR:
                {
                    return 8;
                }
                case DAIR:
                {
                    return 9;
                }
                case BAIR:
                {
                    return 11;
                }
                case FAIR:
                {
                    return 7;
                }
                case NEUTRAL_ATTACK_1:
                {
                    return 7;
                }
                case NEUTRAL_ATTACK_2:
                {
                    return 10;
                }
                case NEUTRAL_B_ATTACKING:
                case NEUTRAL_B_ATTACKING_AIR:
                {
                    return 21;
                }
                case EDGE_ATTACK_SLOW:
                {
                    return 41;
                }
                case EDGE_ATTACK_QUICK:
                {
                    return 28;
                }
                case GROUND_ATTACK_UP:
                {
                    return 31;
                }
                default:
                {
                    return 0;
                    break;
                }
            }
            break;
        }
        default:
        {
            return 0;
            break;
        }
    }
}


uint GameState::landingLag(CHARACTER character, ACTION action)
{
    switch(character)
    {
        case MARTH:
        {
            switch(action)
            {
                case NAIR:
                {
                    return 7;
                }
                case FAIR:
                {
                    return 7;
                }
                case BAIR:
                {
                    return 12;
                }
                case UAIR:
                {
                    return 7;
                }
                case DAIR:
                {
                    return 16;
                }
                default:
                {
                    return 0;
                }
            }
        }
        default:
        {
            return 0;
        }
    }
}

uint GameState::totalActionFrames(CHARACTER character, ACTION action)
{
    switch(character)
    {
        case MARTH:
        {
            switch(action)
            {
                case FSMASH_MID:
                {
                    return 47;
                }
                case DOWNSMASH:
                {
                    return 61;
                }
                case UPSMASH:
                {
                    return 45;
                }
                case DASH_ATTACK:
                {
                    return 40;
                }
                case GRAB:
                {
                    return 30;
                }
                case GRAB_RUNNING:
                {
                    return 40;
                }
                case FTILT_HIGH:
                case FTILT_HIGH_MID:
                case FTILT_MID:
                case FTILT_LOW_MID:
                case FTILT_LOW:
                {
                    return 35;
                }
                case UPTILT:
                {
                    return 31;
                }
                case DOWNTILT:
                {
                    return 19;
                }
                case SWORD_DANCE_1_AIR:
                case SWORD_DANCE_1:
                {
                    return 29;
                }
                case SWORD_DANCE_2_HIGH_AIR:
                case SWORD_DANCE_2_MID_AIR:
                case SWORD_DANCE_2_HIGH:
                case SWORD_DANCE_2_MID:
                {
                    return 40;
                }
                case SWORD_DANCE_3_HIGH_AIR:
                case SWORD_DANCE_3_MID_AIR:
                case SWORD_DANCE_3_LOW_AIR:
                case SWORD_DANCE_3_HIGH:
                case SWORD_DANCE_3_MID:
                case SWORD_DANCE_3_LOW:
                {
                    return 46;
                }
                case SWORD_DANCE_4_HIGH:
                case SWORD_DANCE_4_MID:
                case SWORD_DANCE_4_HIGH_AIR:
                case SWORD_DANCE_4_MID_AIR:
                {
                    return 50;
                }
                case SWORD_DANCE_4_LOW:
                case SWORD_DANCE_4_LOW_AIR:
                {
                    return 60;
                }
                case UP_B:
                case UP_B_GROUND:
                {
                    return 10;
                }
                case NAIR:
                {
                    return 21;
                }
                case UAIR:
                {
                    return 25;
                }
                case DAIR:
                {
                    return 48;
                }
                case BAIR:
                {
                    return 32;
                }
                case FAIR:
                {
                    return 27;
                }
                case NEUTRAL_ATTACK_1:
                {
                    return 19;
                }
                case NEUTRAL_ATTACK_2:
                {
                    return 19;
                }
                case NEUTRAL_B_ATTACKING:
                case NEUTRAL_B_ATTACKING_AIR:
                {
                    return 44;
                }
                case EDGE_ATTACK_SLOW:
                {
                    return 68;
                }
                case EDGE_ATTACK_QUICK:
                {
                    return 54;
                }
                case LANDING_SPECIAL:
                {
                    if(m_landingFromUpB)
                    {
                        return 30;
                    }
                    else
                    {
                        return 10;
                    }
                }
                case MARTH_COUNTER_FALLING:
                case MARTH_COUNTER:
                {
                    return 59;
                }
                case SPOTDODGE:
                {
                    return 27;
                }
                case ROLL_FORWARD:
                case ROLL_BACKWARD:
                {
                    return 35;
                }
                case EDGE_ROLL_SLOW:
                {
                    return 98;
                }
                case EDGE_ROLL_QUICK:
                {
                    return 48;
                }
                case EDGE_GETUP_SLOW:
                {
                    return 58;
                }
                case EDGE_GETUP_QUICK:
                {
                    return 32;
                }
                case NEUTRAL_GETUP:
                {
                    return 30;
                }
                case NEUTRAL_TECH:
                {
                    return 26;
                }
                case FORWARD_TECH:
                {
                    return 40;
                }
                case BACKWARD_TECH:
                {
                    return 40;
                }
                case GETUP_ATTACK:
                {
                    return 23;
                }
                case TECH_MISS_UP:
                {
                    return 25; //TODO This is actually 26... but it starts at 0, so the calculation gets screwed up
                }
                case TECH_MISS_DOWN:
                {
                    return 26;
                }
                case GROUND_ROLL_BACKWARD_UP:
                case GROUND_ROLL_FORWARD_UP:
                case GROUND_ROLL_FORWARD_DOWN:
                case GROUND_ROLL_BACKWARD_DOWN:
                {
                    return 35;
                }
                case GROUND_GETUP:
                {
                    return 30;
                }
                case GROUND_ATTACK_UP:
                {
                    return 49;
                }
                default:
                {
                    return 0;
                    break;
                }
            }
            break;
        }
        case FOX:
        {
            switch(action)
            {
                case THROW_DOWN:
                {
                    return 43;
                }
                case LANDING_SPECIAL:
                {
                    if(m_landingFromUpB)
                    {
                        return 30;
                    }
                    else
                    {
                        return 10;
                    }
                }
                default:
                {
                    return 0;
                }
            }
        }
        default:
        {
            return 0;
            break;
        }
    }
}

void GameState::setLandingState(bool state)
{
    m_landingFromUpB = state;
}

bool GameState::isAttacking(ACTION action)
{
    switch(action)
    {
        case FSMASH_MID:
        case DOWNSMASH:
        case UPSMASH:
        case DASH_ATTACK:
        case GRAB:
        case GRAB_RUNNING:
        case FTILT_HIGH:
        case FTILT_HIGH_MID:
        case FTILT_MID:
        case FTILT_LOW_MID:
        case FTILT_LOW:
        case UPTILT:
        case DOWNTILT:
        case SWORD_DANCE_1:
        case SWORD_DANCE_2_HIGH:
        case SWORD_DANCE_2_MID:
        case SWORD_DANCE_3_HIGH:
        case SWORD_DANCE_3_MID:
        case SWORD_DANCE_3_LOW:
        case SWORD_DANCE_4_HIGH:
        case SWORD_DANCE_4_MID:
        case SWORD_DANCE_4_LOW:
        case SWORD_DANCE_1_AIR:
        case SWORD_DANCE_2_HIGH_AIR:
        case SWORD_DANCE_2_MID_AIR:
        case SWORD_DANCE_3_HIGH_AIR:
        case SWORD_DANCE_3_MID_AIR:
        case SWORD_DANCE_3_LOW_AIR:
        case SWORD_DANCE_4_HIGH_AIR:
        case SWORD_DANCE_4_MID_AIR:
        case SWORD_DANCE_4_LOW_AIR:
        case UP_B:
        case UP_B_GROUND:
        case NAIR:
        case UAIR:
        case DAIR:
        case BAIR:
        case FAIR:
        case NEUTRAL_ATTACK_1:
        case NEUTRAL_ATTACK_2:
        case NEUTRAL_ATTACK_3:
        case NEUTRAL_B_ATTACKING:
        case NEUTRAL_B_ATTACKING_AIR:
        case EDGE_ATTACK_QUICK:
        case EDGE_ATTACK_SLOW:
        case GROUND_ATTACK_UP:
        {
            return true;
        }
        default:
        {
            return false;
        }
    }
}

bool GameState::isReverseHit(ACTION action)
{
    switch(action)
    {
        case DOWNSMASH:
        case UPSMASH:
        case GRAB_RUNNING:
        case UPTILT:
        case NAIR:
        case UAIR:
        case DAIR:
        case BAIR:
        case GROUND_ATTACK_UP:
        {
            return true;
        }
        default:
        {
            return false;
        }
    }
}

bool GameState::isRollingState(ACTION action)
{
    switch(action)
    {
        case ROLL_FORWARD:
        case ROLL_BACKWARD:
        case SPOTDODGE:
        case EDGE_ROLL_SLOW:
        case EDGE_ROLL_QUICK:
        case EDGE_GETUP_SLOW:
        case EDGE_GETUP_QUICK:
        case NEUTRAL_GETUP:
        case NEUTRAL_TECH:
        case FORWARD_TECH:
        case BACKWARD_TECH:
        case MARTH_COUNTER_FALLING:
        case MARTH_COUNTER:
        case TECH_MISS_UP:
        case TECH_MISS_DOWN:
        case GROUND_ROLL_BACKWARD_UP:
        case GROUND_ROLL_FORWARD_UP:
        case GROUND_ROLL_FORWARD_DOWN:
        case GROUND_ROLL_BACKWARD_DOWN:
        case GROUND_GETUP:
        {
            return true;
        }
        default:
        {
            return false;
        }
    }
}

bool GameState::isGrabbedState(ACTION action)
{
    switch(action)
    {
        case GRAB_PULL:
        case GRABBED:
        case SPOTDODGE:
        case GRAB_PUMMELED:
        case GRAB_ESCAPE:
        {
            return true;
        }
        default:
        {
            return false;
        }
    }
}

double GameState::calculateSlideDistance(CHARACTER character, double initSpeed, int frames)
{
    double slideCoeficient;

    switch (character)
    {
        case FOX:
        {
            slideCoeficient = FOX_SLIDE_COEFICIENT;
            break;
        }
        case MARTH:
        {
            slideCoeficient = MARTH_SLIDE_COEFICIENT;
            break;
        }
        default:
        {
            //Probably good enough until all characters are supported
            slideCoeficient = 0.05;
        }
    }

    //This detedmines magnitude of slide
    double slideDistance = 0;
    for(int i = 1; i <= frames; i++)
    {
        slideDistance += std::max(std::abs(initSpeed) - (i * slideCoeficient), 0.0);
    }

    //Determine direction
    if(initSpeed < 0)
    {
        return (-1) * slideDistance;
    }
    return slideDistance;
}

double GameState::getRollDistance(CHARACTER character, ACTION action)
{
    switch (character)
    {
        case MARTH:
        {
            switch(action)
            {
                case ROLL_FORWARD:
                case ROLL_BACKWARD:
                {
                    return 38.95;
                }
                case EDGE_ROLL_SLOW:
                case EDGE_ROLL_QUICK:
                {
                    return 41.44;
                }
                case EDGE_GETUP_SLOW:
                case EDGE_GETUP_QUICK:
                {
                    return 11.33;
                }
                case FORWARD_TECH:
                case BACKWARD_TECH:
                {
                    return 46.711546;//new
                }
                case GROUND_ROLL_FORWARD_UP:
                {
                    return 36.67;
                }
                case GROUND_ROLL_BACKWARD_UP:
                {
                    return 35.83;
                }
                case GROUND_ROLL_FORWARD_DOWN:
                {
                    return 34.65;
                }
                case GROUND_ROLL_BACKWARD_DOWN:
                {
                    return 34.66;
                }
                case NEUTRAL_TECH:
                {
                    return 5.93;
                }
                default:
                {
                    return 0;
                }
            }
        }
        case FOX:
        {
            switch(action)
            {
                case ROLL_FORWARD:
                case ROLL_BACKWARD:
                {
                    return 33.6;
                }
                default:
                {
                    return 0;
                }
            }
        }
        default:
        {
            return 0;
        }
    }
}

bool GameState::getRollDirection(ACTION action)
{
    switch(action)
    {
        case ROLL_FORWARD:
        case EDGE_ROLL_SLOW:
        case EDGE_ROLL_QUICK:
        case EDGE_GETUP_SLOW:
        case EDGE_GETUP_QUICK:
        case FORWARD_TECH:
        case GROUND_ROLL_FORWARD_UP:
        case GROUND_ROLL_FORWARD_DOWN:
        {
            return true;
        }
        case ROLL_BACKWARD:
        case BACKWARD_TECH:
        case GROUND_ROLL_BACKWARD_UP:
        case GROUND_ROLL_BACKWARD_DOWN:
        case NEUTRAL_TECH:
        {
            return false;
        }
        default:
        {
            return true;
        }
    }
}

uint GameState::trailingVulnerableFrames(CHARACTER character, ACTION action)
{
    switch (character)
    {
        case MARTH:
        {
            switch(action)
            {
                case EDGE_GETUP_QUICK:
                {
                    return 2;
                }
                case EDGE_GETUP_SLOW:
                {
                    return 3;
                }
                case MARTH_COUNTER:
                {
                    return 29;
                }
                case GROUND_ROLL_BACKWARD_DOWN:
                {
                    return 5; //TODO: this is a guess
                }
                case GROUND_ATTACK_UP:
                {
                    return 5;
                }
                default:
                {
                    return 7;
                }
            }
        }
        default:
        {
            return 0;
        }
    }
}

bool GameState::hasMultipleHitboxes(CHARACTER character, ACTION action)
{
    switch(character)
    {
        case MARTH:
        {
            switch(action)
            {
                case SWORD_DANCE_4_LOW:
                case SWORD_DANCE_4_LOW_AIR:
                case GROUND_ATTACK_UP:
                {
                    return true;
                }
                default:
                {
                    return false;
                }
            }
            break;
        }
        default:
        {
            return false;
        }
    }
}
