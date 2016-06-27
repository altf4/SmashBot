#include <cmath>
#include <math.h>

#include "Bait.h"
#include "../Util/Constants.h"
#include "../Util/Logger.h"
#include "../Tactics/Approach.h"
#include "../Tactics/CreateDistance.h"
#include "../Tactics/KeepDistance.h"
#include "../Tactics/Wait.h"
#include "../Tactics/Parry.h"
#include "../Tactics/ShineCombo.h"
#include "../Tactics/Laser.h"
#include "../Tactics/Edgeguard.h"
#include "../Tactics/Recover.h"
#include "../Tactics/Punish.h"
#include "../Tactics/ShowOff.h"
#include "../Tactics/Escape.h"
#include "../Tactics/TechChase.h"

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
    //Logger::Instance()->Log(INFO, "");

    Logger::Instance()->Log(INFO, "player_one_speed_x_attack: " + std::to_string(m_state->m_memory->player_one_speed_x_attack));
    Logger::Instance()->Log(INFO, "player_one_speed_air_x_self: " + std::to_string(m_state->m_memory->player_one_speed_air_x_self));
    Logger::Instance()->Log(INFO, "player_one_speed_y_self: " + std::to_string(m_state->m_memory->player_one_speed_y_self));

    //Has opponent just released a charged smash attack?
    bool chargedSmashReleased = false;
    if(!m_state->m_memory->player_one_charging_smash && m_chargingLastFrame)
    {
        chargedSmashReleased = true;
    }
    m_chargingLastFrame = m_state->m_memory->player_one_charging_smash;

    //Update the attack frame if the enemy started a new action
    if(m_state->m_memory->player_one_action_frame == 1)
    {
        m_shieldedAttack = false;
        m_actionChanged = true;
    }
    //Continuing same previous action
    else
    {
        m_actionChanged = false;
        if(m_state->m_memory->player_two_action == SHIELD_STUN ||
            m_state->m_memory->player_two_action == SPOTDODGE ||
            m_state->m_memory->player_two_action == EDGE_GETUP_QUICK ||
            m_state->m_memory->player_two_action == EDGE_GETUP_SLOW)
        {
            m_shieldedAttack = true;
        }
    }

    //Escape out of our opponents combo / grab if they somehow get it
    // This even takes precedence over uninterruptible chains (because they got interrupted anyway)
    if(m_state->isDamageState((ACTION)m_state->m_memory->player_two_action) ||
        m_state->isGrabbedState((ACTION)m_state->m_memory->player_two_action) ||
        m_state->m_memory->player_two_action == TUMBLING)
    {
        CreateTactic(Escape);
        m_tactic->DetermineChain();
        return;
    }

    //If we're not in a state to interupt, just continue with what we've got going
    if((m_tactic != NULL) && (!m_tactic->IsInterruptible()))
    {
        m_tactic->DetermineChain();
        return;
    }

    //If we're still warping in at the start of the match or in shield stun, then just hang out and do nothing
    if(m_state->m_memory->player_two_action == ENTRY ||
        m_state->m_memory->player_two_action == ENTRY_START ||
        m_state->m_memory->player_two_action == ENTRY_END ||
        m_state->m_memory->player_two_action == SHIELD_STUN ||
        m_state->m_memory->player_two_action == LANDING_SPECIAL ||
        m_state->m_memory->player_two_action == WAVEDASH_SLIDE ||
        m_state->m_memory->player_two_action == SPOTDODGE ||
        m_state->m_memory->player_two_action == SHIELD_STUN ||
        m_state->m_memory->player_two_action == EDGE_CATCHING ||
        m_state->isRollingState((ACTION)m_state->m_memory->player_two_action) ||
        m_state->m_memory->player_two_action == THROW_FORWARD ||
        m_state->m_memory->player_two_action == THROW_BACK ||
        m_state->m_memory->player_two_action == THROW_UP ||
        m_state->m_memory->player_two_action == THROW_DOWN)
    {
        //If we're in the last frame of the action, then we're free to do whatever
        uint totalActionFrames = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_two_character,
            (ACTION)m_state->m_memory->player_two_action);
        if(m_state->m_memory->player_two_action_frame != totalActionFrames)
        {
            CreateTactic(Wait);
            m_tactic->DetermineChain();
            return;
        }
    }

    //Calculate distance between players
    double distance = pow(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x, 2);
    distance += pow(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y, 2);
    distance = sqrt(distance);

    bool isLoopingAttack = m_state->m_memory->player_one_action == NEUTRAL_ATTACK_1 ||
        m_state->m_memory->player_one_action == NEUTRAL_ATTACK_2 ||
        m_state->m_memory->player_one_action == DOWNTILT;

    //MArth leans WAY in during jabs. The distance should be adjusted
    if(isLoopingAttack)
    {
        distance -= 5;
    }

    if(m_state->m_memory->player_two_on_ground)
    {
        //If we're able to punish our opponent, let's do that
        if(m_state->m_memory->player_one_action == SPOTDODGE ||
            m_state->m_memory->player_one_action == MARTH_COUNTER ||
            m_state->m_memory->player_one_action == MARTH_COUNTER_FALLING ||
            m_state->m_memory->player_one_action == LANDING_SPECIAL ||
            m_state->m_memory->player_one_action == WAVEDASH_SLIDE ||
            m_state->m_memory->player_one_action == TECH_MISS_UP ||
            m_state->m_memory->player_one_action == TECH_MISS_DOWN)
        {
            if(m_actionChanged)
            {
                delete m_tactic;
                m_tactic = NULL;
            }
            if(m_state->m_memory->player_one_percent > MARTH_UPSMASH_KILL_PERCENT)
            {
                CreateTactic(Punish);
                m_tactic->DetermineChain();
                return;
            }
            else
            {
                CreateTactic(TechChase);
                m_tactic->DetermineChain();
                return;
            }
        }

        bool player_two_is_to_the_left = (m_state->m_memory->player_two_x - m_state->m_memory->player_one_x > 0);
        //If our opponent is stuck in the windup for an attack, let's hit them with something harder than shine
        if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
            m_state->m_memory->player_one_action != GROUND_ATTACK_UP && //Can't punish before the attack on a getup attack
            distance < FOX_UPSMASH_RANGE-2 &&
            m_state->m_memory->player_two_facing != player_two_is_to_the_left &&
            std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + .001)
        {
            //How many frames do we have until the attack lands? If it's at least 3, then we can start a Punish
            int frames_left = m_state->firstHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
                (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;
            if(frames_left > 7)
            {
                if(m_actionChanged)
                {
                    delete m_tactic;
                    m_tactic = NULL;
                }
                CreateTactic(Punish);
                m_tactic->DetermineChain();
                return;
            }
        }

        //If they're lying on the ground, techchase them
        if(m_state->m_memory->player_one_action == LYING_GROUND_UP ||
            m_state->m_memory->player_one_action == LYING_GROUND_DOWN)
        {
            if(m_actionChanged)
            {
                delete m_tactic;
                m_tactic = NULL;
            }
            CreateTactic(TechChase);
            m_tactic->DetermineChain();
            return;
        }

        //If we're hanging on the egde, and they are falling above the stage, punish it
        if(m_state->m_memory->player_one_action == DEAD_FALL &&
            m_state->m_memory->player_two_action == EDGE_HANGING &&
            std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + .001)
        {
            if(m_actionChanged)
            {
                delete m_tactic;
                m_tactic = NULL;
            }
            CreateTactic(Punish);
            m_tactic->DetermineChain();
            return;
        }

        //How many frames do we have until the attack is over?
        int frames_left = m_state->totalActionFrames((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

        uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
            (ACTION)m_state->m_memory->player_one_action);

        //If enemy is in hit stun
        if(m_state->isDamageState((ACTION)m_state->m_memory->player_one_action))
        {
            frames_left = m_state->m_memory->player_one_hitstun_frames_left;
        }

        //You can actually get pushed over the bundaries of the stage a bit here. But that's fine
        bool onStage = std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + .001;
        onStage = onStage || (std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + 3.0 &&
            m_state->m_memory->player_one_on_ground);
        //Let's consider the opponent "on stage" if they're rolling on
        onStage = onStage || (m_state->m_memory->player_one_action == EDGE_ROLL_SLOW ||
            m_state->m_memory->player_one_action == EDGE_ROLL_QUICK ||
            m_state->m_memory->player_one_action == EDGE_GETUP_SLOW ||
            m_state->m_memory->player_one_action == EDGE_GETUP_QUICK ||
            m_state->m_memory->player_one_action == EDGE_ATTACK_QUICK ||
            m_state->m_memory->player_one_action == EDGE_ATTACK_SLOW);

        //If our oponnent is stuck in a laggy ending animation (on stage), punish it
        //Rolling or ending an attack
        if(onStage  &&
            (m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) ||
            m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) ||
            (m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
            (m_state->m_memory->player_one_action_frame > lastHitboxFrame || lastHitboxFrame == 0))))
        {
            //Can we get an attack in time?
            if(frames_left > 7 ||
                (m_state->m_memory->player_two_action == SHIELD_RELEASE && frames_left > 15))
            {
                if(m_actionChanged)
                {
                    delete m_tactic;
                    m_tactic = NULL;
                }
                if(m_state->m_memory->player_one_percent >= MARTH_UPSMASH_KILL_PERCENT)
                {
                    CreateTactic(Punish);
                    m_tactic->DetermineChain();
                    return;
                }
                else
                {
                    CreateTactic(TechChase);
                    m_tactic->DetermineChain();
                    return;
                }
            }
        }
    }

    //If we're able to shine p1 right now, let's do that
    if(std::abs(distance) < FOX_SHINE_RADIUS)
    {
        //Are we in a state where we can shine?
        if(ReadyForAction(m_state->m_memory->player_two_action))
        {
            //Is the opponent in a state where they can get hit by shine?
            if(m_state->m_memory->player_one_action != SHIELD &&
                m_state->m_memory->player_one_action != SHIELD_REFLECT &&
                m_state->m_memory->player_one_action != SHIELD_START &&
                m_state->m_memory->player_one_action != SHIELD_STUN &&
                m_state->m_memory->player_one_action != MARTH_COUNTER &&
                m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING &&
                m_state->m_memory->player_one_action != EDGE_CATCHING &&
                m_state->m_memory->player_one_action != SPOTDODGE &&
                m_state->m_memory->player_one_action != GROUND_ATTACK_UP && //Can't punish before the attack on a getup attack
                m_state->m_memory->player_one_action != TECH_MISS_UP && //We CAN shine these. But we choose not to.
                m_state->m_memory->player_one_action != TECH_MISS_DOWN  //Since there's a better
                )
            {
                CreateTactic(ShineCombo);
                m_tactic->DetermineChain();
                return;
            }
        }
    }

    //If we're in shield release, but can't punish safely, then just get out of there
    //NOTE: Do not put any punish tactics below here.
    if(m_state->m_memory->player_two_action == SHIELD_RELEASE)
    {
        CreateTactic(CreateDistance);
        m_tactic->DetermineChain();
        return;
    }

    //If we're hanging on the egde, and the oponnent is on the stage area, then recover
    if((m_state->m_memory->player_two_action == EDGE_HANGING ||
        m_state->m_memory->player_two_action == EDGE_CATCHING) &&
        std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() + .001 &&
        m_state->m_memory->player_one_y > -5)
    {
        CreateTactic(Recover);
        m_tactic->DetermineChain();
        return;
    }

    bool multipleHitboxes = m_state->hasMultipleHitboxes((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    //TODO: This is really kludgey and horrible. Replace this eventually with the solution to:
    // https://github.com/altf4/SmashBot/issues/58
    bool isUnderDolphinSlash = m_state->m_memory->player_one_y < m_state->m_memory->player_two_y &&
        m_state->m_memory->player_one_action == UP_B &&
        std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x) < 25;

    double attackRange = MARTH_FSMASH_RANGE;
    if(isLoopingAttack)
    {
        //Really kludgey range adjustment
        attackRange = MARTH_JAB_RANGE-5;
    }

    //If we need to defend against an attack, that's next priority. Unless we've already shielded this attack
    if((!m_shieldedAttack || multipleHitboxes) &&
        (distance < attackRange || isUnderDolphinSlash))
    {
        //Don't bother parrying if the attack is over
        if(m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character, (ACTION)m_state->m_memory->player_one_action) >=
            m_state->m_memory->player_one_action_frame)
        {
            //Don't bother parrying if the attack is in the wrong direction
            bool player_one_is_to_the_left = (m_state->m_memory->player_one_x - m_state->m_memory->player_two_x > 0);
            bool opponentFacingUs = m_state->m_memory->player_one_facing != player_one_is_to_the_left;
            //If the opponent is under the stage, hitboxes get weird. Let's always consider it facing us
            opponentFacingUs = opponentFacingUs || (m_state->m_memory->player_one_y < 0);

            if((opponentFacingUs || m_state->isReverseHit((ACTION)m_state->m_memory->player_one_action)) &&
                (m_state->m_memory->player_two_on_ground ||
                m_state->m_memory->player_two_action == EDGE_HANGING ||
                m_state->m_memory->player_two_action == EDGE_CATCHING))
            {
                //Don't bother parrying if we're going to be invincible for the attack
                int invincibilityFramesLeft = 29 - (m_state->m_memory->frame - m_state->m_edgeInvincibilityStart);
                int framesUntilAttack = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
                    (ACTION)m_state->m_memory->player_one_action) - m_state->m_memory->player_one_action_frame;

                if(framesUntilAttack > invincibilityFramesLeft)
                {
                    if(m_state->isAttacking((ACTION)m_state->m_memory->player_one_action))
                    {
                        //If the p1 action changed, scrap the old Parry and make a new one.
                        if(m_actionChanged || chargedSmashReleased)
                        {
                            delete m_tactic;
                            m_tactic = NULL;
                        }

                        CreateTactic(Parry);
                        m_tactic->DetermineChain();
                        return;
                    }
                }
            }
        }
    }

    //If the enemy is dead, then celebrate!
    if(m_state->m_memory->player_one_y < MARTH_LOWER_EVENT_HORIZON ||
        (m_state->m_memory->player_one_action >= DEAD_DOWN &&
        m_state->m_memory->player_one_action <= DEAD_FLY_SPLATTER_FLAT) ||
        (m_state->m_memory->player_one_action == DEAD_FALL &&
         m_state->m_memory->player_one_y < -20))
    {
        //Have to be on the ground or on edge
        if(m_state->m_memory->player_two_on_ground ||
            m_state->m_memory->player_two_action == EDGE_HANGING ||
            m_state->m_memory->player_two_action == EDGE_CATCHING ||
            m_state->m_memory->player_two_action == DOWN_B_STUN ||
            m_state->m_memory->player_two_action == DOWN_B_AIR)
        {
            CreateTactic(ShowOff);
            m_tactic->DetermineChain();
            return;
        }
    }

    bool opponentOnStage = m_state->m_memory->player_one_on_ground ||
        (std::abs(m_state->m_memory->player_one_x) < m_state->getStageEdgeGroundPosition() &&
        m_state->m_memory->player_one_y > -5);
    bool selfOnStage = m_state->m_memory->player_two_on_ground ||
        (std::abs(m_state->m_memory->player_two_x) < m_state->getStageEdgeGroundPosition() &&
        m_state->m_memory->player_two_y > -5);

    //Logger::Instance()->Log(INFO, "opponentOnStage: ");

    //If we're both off the stage...
    if(!opponentOnStage &&
        !selfOnStage)
    {
        //If we're able to shine opponent right now, let's do that
        if(std::abs(distance) < FOX_SHINE_RADIUS &&
            !m_state->m_memory->player_one_invulnerable &&
            m_state->m_memory->player_one_action != AIRDODGE &&
            m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING)
        {
            CreateTactic(Edgeguard);
            m_tactic->DetermineChain();
            return;
        }

        //If we're already on the edge, just stay there
        if(m_state->m_memory->player_two_action != EDGE_CATCHING &&
            m_state->m_memory->player_two_action != EDGE_HANGING)
        {
            //Opponent is in a damage state, then just recover. We already hit them.
            //Or if we're below the opponent
            if(m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) ||
                m_state->m_memory->player_one_y > m_state->m_memory->player_two_y + 8)
            {
                CreateTactic(Recover);
                m_tactic->DetermineChain();
                return;
            }
        }
    }

    //If the opponent is off the stage, let's edgeguard them
    //NOTE: Sometimes players can get a little below 0 in Y coordinates without being off the stage
    if(!m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) &&
        ((std::abs(m_state->m_memory->player_one_x) > m_state->getStageEdgeGroundPosition() + .001 && !m_state->m_memory->player_one_on_ground) ||
        m_state->m_memory->player_one_y < -5.5 ||
        m_state->m_memory->player_one_action == EDGE_CATCHING ||
        m_state->m_memory->player_one_action == EDGE_HANGING))
    {
        CreateTactic(Edgeguard);
        m_tactic->DetermineChain();
        return;
    }

    //If we're off the stage and don't need to edgeguard, get back on
    if(std::abs(m_state->m_memory->player_two_x) > m_state->getStageEdgeGroundPosition() + .001)
    {
        CreateTactic(Recover);
        m_tactic->DetermineChain();
        return;
    }

    //If we're far away, just laser
    // But stop once enemy is at kill percent
    if(std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x) > 90 &&
        std::abs(m_state->m_memory->player_one_x) < 130 &&
        std::abs(m_state->m_memory->player_two_x) < m_state->getStageEdgeGroundPosition() &&
        std::abs(m_state->m_memory->player_one_percent) < MARTH_UPSMASH_KILL_PERCENT)
    {
        CreateTactic(Laser);
        m_tactic->DetermineChain();
        return;
    }

    uint lastHitboxFrame = m_state->lastHitboxFrame((CHARACTER)m_state->m_memory->player_one_character,
        (ACTION)m_state->m_memory->player_one_action);

    bool afterAttack = m_state->isAttacking((ACTION)m_state->m_memory->player_one_action) &&
        m_state->m_memory->player_one_action_frame > lastHitboxFrame;

    //Specifically for Marth's jabs, don't approach unless we start just at the right time
    if(isLoopingAttack &&
        m_state->m_memory->player_one_action_frame == lastHitboxFrame)
    {
        CreateTactic2(Approach, false);
        m_tactic->DetermineChain();
        return;
    }
    else
    {
         afterAttack = false;
    }

    //If our opponent is doing something to put them in a vulnerable spot, approach
    if(m_state->m_memory->player_one_action == KNEE_BEND ||
        m_state->m_memory->player_one_action == JUMPING_FORWARD ||
        m_state->m_memory->player_one_action == JUMPING_BACKWARD ||
        m_state->m_memory->player_one_action == SHIELD ||
        m_state->m_memory->player_one_action == SHIELD_START ||
        m_state->m_memory->player_one_action == SHIELD_REFLECT ||
        m_state->m_memory->player_one_action == NAIR_LANDING ||
        m_state->m_memory->player_one_action == FAIR_LANDING ||
        m_state->m_memory->player_one_action == UAIR_LANDING ||
        m_state->m_memory->player_one_action == BAIR_LANDING ||
        m_state->m_memory->player_one_action == DAIR_LANDING ||
        m_state->m_memory->player_one_action == AIRDODGE ||
        m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) ||
        m_state->isRollingState((ACTION)m_state->m_memory->player_one_action) ||
        afterAttack)
    {
        CreateTactic2(Approach, true);
        m_tactic->DetermineChain();
        return;
    }

    bool onRight = m_state->m_memory->player_one_x < m_state->m_memory->player_two_x;

    //If our opponent is dashing toward us, approach
    if(m_state->m_memory->player_one_action == DASHING &&
        m_state->m_memory->player_one_facing == onRight)
    {
        CreateTactic2(Approach, true);
        m_tactic->DetermineChain();
        return;
    }

    //Before keeping our distance any longer, consider randomly approaching once per dash dance
    if(m_state->m_memory->player_two_action == DASHING &&
        m_state->m_memory->player_two_action_frame == 1 &&
        m_state->m_memory->player_two_facing != onRight &&
        rand() % 8 == 0)
    {
        CreateTactic2(Approach, false);
        m_tactic->DetermineChain();
        return;
    }

    CreateTactic(KeepDistance);
    m_tactic->DetermineChain();
    return;
}
