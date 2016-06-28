#include <cmath>
#include <math.h>

#include "Edgeguard.h"
#include "../Util/Constants.h"
#include "../Chains/Nothing.h"
#include "../Chains/JumpCanceledShine.h"
#include "../Chains/GrabEdge.h"
#include "../Chains/EdgeAction.h"
#include "../Chains/DI.h"
#include "../Chains/MarthKiller.h"
#include "../Chains/Waveshine.h"
#include "../Chains/EdgeStall.h"
#include "../Chains/DashDance.h"
#include "../Chains/FireFox.h"
#include "../Util/Controller.h"
#include "../Util/Logger.h"

Edgeguard::Edgeguard()
{
    m_chain = NULL;
}

Edgeguard::~Edgeguard()
{
    delete m_chain;
}

void Edgeguard::DetermineChain()
{
    //If we're not in a state to interupt, just continue with what we've got going
    if((m_chain != NULL) && (!m_chain->IsInterruptible()))
    {
        m_chain->PressButtons();
        return;
    }

    double lowerEventHorizon = MARTH_LOWER_EVENT_HORIZON;
    if(m_state->m_memory->player_one_jumps_left == 0 &&
        m_state->m_memory->player_one_speed_y_self > 0)
    {
        double jumpHeight = m_state->calculateDoubleJumpHeight((CHARACTER)m_state->m_memory->player_one_character,
            m_state->m_memory->player_one_speed_y_self);
        lowerEventHorizon += jumpHeight;
    }

    if(m_state->m_memory->player_two_action == EDGE_CATCHING)
    {
        CreateChain(Nothing);
        m_chain->PressButtons();
        return;
    }

    //Marth is dead if he's at this point
    if(m_state->m_memory->player_one_y < lowerEventHorizon)
    {
        if(m_state->m_memory->player_two_action == EDGE_HANGING)
        {
            CreateChain2(EdgeAction, STAND_UP);
            m_chain->PressButtons();
            return;
        }
        if(m_state->m_memory->player_two_on_ground)
        {
            //Start moving to center stage
            CreateChain3(DashDance, 0, 0);
            m_chain->PressButtons();
            return;
        }
    }

    //Edgehog our opponent if they're UP-B'ing sweetspotted.
    //Grab the edge if we're still on the stage
    if(m_state->m_memory->player_one_action == UP_B &&
        m_state->m_memory->player_two_action == EDGE_HANGING)
    {
        double doubleJumpHeight = m_state->getDoubleJumpHeightMax((CHARACTER)m_state->m_memory->player_one_character);
        //Is marth so low that he must grab the edge? If so, just roll up.
        if(m_state->m_memory->player_one_y < MARTH_RECOVER_HIGH_EVENT_HORIZON + doubleJumpHeight)
        {
            CreateChain3(EdgeAction, ROLL_UP, 2);
            m_chain->PressButtons();
            return;
        }
        //If not, he might land on the stage. So, just stand up and attack on the other end
        else
        {
            CreateChain2(EdgeAction, STAND_UP);
            m_chain->PressButtons();
            return;
        }
    }

    //distance formula
    double distance = pow(std::abs(m_state->m_memory->player_one_x - m_state->m_memory->player_two_x), 2);
    distance += pow(std::abs(m_state->m_memory->player_one_y - m_state->m_memory->player_two_y), 2);
    distance = sqrt(distance);

    double edge_distance_x = std::abs(std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition());
    double edge_distance_y = std::abs(m_state->m_memory->player_one_y - EDGE_HANGING_Y_POSITION);

    //Are they close enough and falling downwards?
    bool canOpponentGrabEdge = m_state->m_memory->player_one_y > -EDGE_MAGNETISM_Y && //Kludgey number. Make this more elegant
        edge_distance_x < EDGE_MAGNETISM_X &&
        m_state->m_memory->player_one_speed_y_self < 0;

    bool inShine = m_state->m_memory->player_two_action == DOWN_B_GROUND ||
        m_state->m_memory->player_two_action == DOWN_B_STUN ||
        m_state->m_memory->player_two_action == DOWN_B_GROUND_START ||
        m_state->m_memory->player_two_action == DOWN_B_AIR ||
        m_state->m_memory->player_two_action == SHINE_TURN ||
        m_state->m_memory->player_two_action == SHINE_RELEASE_AIR;

    //If we're able to shine p1 right now, let's do that
    if(std::abs(distance) < FOX_SHINE_RADIUS &&
        !canOpponentGrabEdge &&
        !m_state->m_memory->player_one_invulnerable &&
        m_state->m_memory->player_one_action != EDGE_CATCHING &&
        m_state->m_memory->player_one_action != AIRDODGE &&
        m_state->m_memory->player_one_action != MARTH_COUNTER &&
        m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING &&
        !inShine)
    {
        CreateChain(JumpCanceledShine);
        m_chain->PressButtons();
        return;
    }

    //Consider refreshing invincibility if the enemy is getting close
    if(m_state->m_memory->player_two_action == EDGE_HANGING &&
        m_state->m_memory->player_two_action_frame == 1)
    {
        //Let's do some math and see if we can safely edge stall without risk of our opponent grabbing the edge
        // (We will be stuck in this animation for 29 frames, so it's a big commitment)
        bool onRightOfOpponent = m_state->m_memory->player_one_x > m_state->m_memory->player_two_x;

        bool initSpeed = m_state->m_memory->player_one_speed_air_x_self;
        if(m_state->m_memory->player_one_jumps_left > 0)
        {
            initSpeed = m_state->getInitHorizontalAirSpeed((CHARACTER)m_state->m_memory->player_one_character);
            if(!onRightOfOpponent)
            {
                initSpeed *= -1.0;
            }
        }

        //How far at best could the opponent travel in the next 29 frames? (The amount of time it takes to finish the edge stall)
        //TODO: This does not consider the fact that apparently DEAD_FALL has different accellation
        double maxHorizontalDistance = m_state->calculateMaxAirDistance((CHARACTER)m_state->m_memory->player_one_character, initSpeed, 29, onRightOfOpponent);
        double endPositionX = m_state->m_memory->player_one_x + maxHorizontalDistance;
        bool canReachEdgeHorizontal = std::abs(endPositionX) < m_state->getStageEdgePosition() + EDGE_MAGNETISM_X;

        //Can opponent reach the edge vertically?
        bool canReachEdgeVertical = false;
        //Calculate how high they can jump to given their current rates
        double vertSpeed = m_state->m_memory->player_one_speed_y_self;
        if(m_state->m_memory->player_one_jumps_left > 0)
        {
            //If they still have a jump, consider the possibility that they could use it
            vertSpeed = m_state->getInitVerticalAirSpeed((CHARACTER)m_state->m_memory->player_one_character);
        }
        double jumpHeight = m_state->calculateDoubleJumpHeight((CHARACTER)m_state->m_memory->player_one_character, vertSpeed);

        //Does opponent need to jump? (recovering low)
        if(m_state->m_memory->player_one_y < -EDGE_MAGNETISM_Y)
        {
            if(m_state->m_memory->player_one_y + jumpHeight > -EDGE_MAGNETISM_Y &&
                m_state->getFramesUntilFallingFromJump((CHARACTER)m_state->m_memory->player_one_character) < 29)
            {
                canReachEdgeVertical = true;
            }
        }
        else
        {
            //Opponent is above, trying to fall down
            int framesUntilFalling = 0;
            double fallStartHeight = m_state->m_memory->player_one_y;
            if(m_state->m_memory->player_one_action == JUMPING_ARIAL_FORWARD ||
                m_state->m_memory->player_one_action == JUMPING_ARIAL_BACKWARD)
            {
                framesUntilFalling = m_state->getFramesUntilFallingFromJump((CHARACTER)m_state->m_memory->player_one_character) -
                    m_state->m_memory->player_one_action_frame;
                fallStartHeight += jumpHeight;
            }
            int fallingFrames = 29 - framesUntilFalling;
            double fastFallSpeed = m_state->getFastfallSpeed((CHARACTER)m_state->m_memory->player_one_character);

            //Assume a fastfall from the start of the opponent's falling
            if(fallStartHeight - (fallingFrames * fastFallSpeed) < -EDGE_MAGNETISM_Y_TOP)
            {
                 canReachEdgeVertical = true;
            }
        }

        //The oppoent can't read the edge in time
        //NOTE: Technically, this doesn't test that the opponent can reach the x and y positions of the edge at the SAME time
        // So, it might refuse to edge stall conservatively in some rare cases
        if(!canReachEdgeHorizontal || !canReachEdgeVertical)
        {
            //Don't edge stall if opponent can up-b to the edge quickly
            if(edge_distance_y > MARTH_UP_B_HEIGHT + 10 ||
                ((edge_distance_x > MARTH_UP_B_X_DISTANCE) && (std::abs(m_state->m_memory->player_one_x) > m_state->getStageEdgePosition())))
            {
                CreateChain(EdgeStall);
                m_chain->PressButtons();
                return;
            }
        }
    }

    double foxFastFallSpeed = m_state->getFastfallSpeed((CHARACTER)m_state->m_memory->player_two_character);

    //Drop down and shine the enemy if they are below us and we have enough invincibility
    int invincibilityFramesLeft = 29 - (m_state->m_memory->frame - m_state->m_edgeInvincibilityStartSelf);
    if(std::abs(m_state->m_memory->player_two_x - m_state->m_memory->player_one_x) < 7 &&
        (invincibilityFramesLeft * foxFastFallSpeed) > distance &&
        m_state->m_memory->player_two_y > m_state->m_memory->player_one_y &&
        !m_state->m_memory->player_one_on_ground &&
        !m_state->m_memory->player_two_on_ground &&
        !canOpponentGrabEdge &&
        m_state->m_memory->player_one_action != AIRDODGE &&
        m_state->m_memory->player_one_action != MARTH_COUNTER_FALLING &&
        m_state->m_memory->player_one_jumps_left == 0)
    {
        CreateChain2(EdgeAction, FASTFALL);
        m_chain->PressButtons();
        return;
    }

    //Alternatively, we can shine when they are hanging on the edge
    if(std::abs(m_state->getStageEdgeGroundPosition() - std::abs(m_state->m_memory->player_two_x)) < 2 &&
        m_state->m_memory->player_one_action == EDGE_HANGING &&
        !m_state->m_memory->player_one_invulnerable)
    {
        CreateChain(Waveshine);
        m_chain->PressButtons();
        return;
    }

    //If we're still on the stage, see if it's safe to grab the edge
    if(m_state->m_memory->player_two_on_ground)
    {
        //If we're already transitioning into grabbing the edge, then keep going.
        if(m_state->m_memory->player_two_action == KNEE_BEND)
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }

        //If the enemy is in a stunned damage state, go ahead and try.
        if(m_state->isDamageState((ACTION)m_state->m_memory->player_one_action) &&
            m_state->m_memory->player_one_hitstun_frames_left > 15)
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }

        //Calculate distance between players
        double distance = pow(std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition(), 2);
        distance += pow(m_state->m_memory->player_one_y, 2);
        distance = sqrt(distance);

        //If marth is out of attack range and UP-B range, then go ahead and do it
        if(distance > MARTH_FSMASH_RANGE &&
            (std::abs(m_state->m_memory->player_one_x) - m_state->getStageEdgePosition() > MARTH_UP_B_X_DISTANCE + 5 ||
            edge_distance_y > MARTH_UP_B_HEIGHT + 15))
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }

        //If marth is side-B'ing (out of attack range) then it's safe
        if(m_state->m_memory->player_one_action == SWORD_DANCE_1)
        {
            CreateChain(GrabEdge);
            m_chain->PressButtons();
            return;
        }
    }

    //Do the marth killer if we're on the stage and Marth is going to be stuck recovering with an up-B
    if(m_state->m_memory->player_two_on_ground &&
        m_state->m_memory->player_one_y < MARTH_JUMP_ONLY_EVENT_HORIZON)
    {
        CreateChain(MarthKiller);
        m_chain->PressButtons();
        return;
    }

    //Dash dance around the edge
    if((m_state->m_memory->player_one_action == SLIDING_OFF_EDGE ||
        m_state->m_memory->player_one_action == EDGE_CATCHING ||
        m_state->m_memory->player_one_action == EDGE_HANGING) &&
        m_state->m_memory->player_two_on_ground)
    {
        bool onLeft = m_state->m_memory->player_one_x < 0;
        double pivotPoint = onLeft ? (-1) * m_state->getStageEdgeGroundPosition() : m_state->getStageEdgeGroundPosition();
        CreateChain3(DashDance, pivotPoint, 0);
        m_chain->PressButtons();
        return;
    }

    //If we're still on the stage, then dash dance around the edge
    if(m_state->m_memory->player_two_on_ground)
    {
        bool onLeft = m_state->m_memory->player_one_x < 0;
        double pivotPoint = onLeft ? (-1) * m_state->getStageEdgeGroundPosition() : m_state->getStageEdgeGroundPosition();
        CreateChain3(DashDance, pivotPoint, 0);
        m_chain->PressButtons();
        return;
    }

    //Aim at our opponent if we're falling at them
    if(m_state->m_memory->player_two_y > m_state->m_memory->player_one_y &&
        m_state->m_memory->player_two_action == FALLING)
    {
        CreateChain3(DI, m_state->m_memory->player_one_x > m_state->m_memory->player_two_x ? true : false, .5);
        m_chain->PressButtons();
        return;
    }

    double xDistanceToEdge = std::abs(std::abs(m_state->m_memory->player_two_x) - m_state->getStageEdgePosition());
    bool onRight = m_state->m_memory->player_two_x > 0;
    //Can we grab the edge, but are moving upwards?
    if(xDistanceToEdge < 4.5 &&
        m_state->m_memory->player_two_y > -10 &&
        m_state->m_memory->player_two_facing != onRight &&
        m_state->m_memory->player_two_speed_y_self > 0)
    {
        CreateChain2(FireFox, true);
        m_chain->PressButtons();
        return;
    }

    //Just hang out and do nothing
    CreateChain(Nothing);
    m_chain->PressButtons();
    return;
}
