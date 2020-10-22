import melee
import Chains
import math
import random
from melee.enums import Action, Button, Character
from Tactics.tactic import Tactic
from Tactics.punish import Punish
from Tactics.defend import Defend
from Chains.dropdownshine import Dropdownshine

class Edgeguard(Tactic):
    def __init__(self, logger, controller, framedata, difficulty):
        Tactic.__init__(self, logger, controller, framedata, difficulty)
        self.upbstart = 0

    # This is exactly flipped from the recover logic
    def canedgeguard(smashbot_state, opponent_state, gamestate):
        if not smashbot_state.off_stage and opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return True

        if not opponent_state.off_stage:
            return False

        # We can now assume that opponent is off the stage...

        # If smashbot is on stage
        if not smashbot_state.off_stage:
            return True

        # If smashbot is in hitstun, then recover
        if smashbot_state.off_stage and smashbot_state.hitstun_frames_left > 0:
            return True

        # If smashbot is closer to the edge, edgeguard
        diff_x_opponent = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(opponent_state.x))
        diff_x = abs(melee.stages.EDGE_POSITION[gamestate.stage] - abs(smashbot_state.x))

        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        opponent_dist = math.sqrt( (opponent_state.y+15)**2 + (diff_x_opponent)**2 )
        smashbot_dist = math.sqrt( (smashbot_state.y+15)**2 + (diff_x)**2 )

        if smashbot_dist < opponent_dist and not opponentonedge:
            return True
        return False

    def illusionhighframes(self, gamestate, opponent_state):
        inillusion =  opponent_state.character in [Character.FOX, Character.FALCO] and \
            opponent_state.action in [Action.SWORD_DANCE_2_HIGH, Action.SWORD_DANCE_2_MID] and (0 < opponent_state.y < 30)
        if not inillusion:
            return 999
        if not (-2 < opponent_state.y < 25):
            return 999

        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.x < 0:
            edge_x = -edge_x

        speed = 16.5
        if opponent_state.character == Character.FOX:
            speed = 18.72

        if opponent_state.x > 0:
            speed = -speed

        x = opponent_state.x
        frames = 0
        for i in range(1, 3):
            x += speed
            if abs(edge_x - x) < 10:
                frames = i

        if frames == 0:
            return 999

        # Plus the windup frames
        if opponent_state.action == Action.SWORD_DANCE_2_HIGH:
            frames += self.framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame + 1

        return frames

    # Is opponent trying to firefox above the stage?
    def firefoxhighframes(self, gamestate, opponent_state):
        firefox = opponent_state.action in [Action.SWORD_DANCE_4_HIGH, Action.SWORD_DANCE_4_MID] and opponent_state.character in [Character.FOX, Character.FALCO]
        if not firefox:
            return 999

        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        if opponent_state.x < 0:
            edge_x = -edge_x

        x, y = opponent_state.x, opponent_state.y
        # Project their trajectory. Does it reach right above the edge? When will it?
        for i in range(self.framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame):
            x += opponent_state.speed_air_x_self
            y+= opponent_state.speed_y_self
            if abs(edge_x - x) < 10 and 0 < y < 25:
                return i

        return 999

    def canrecoverhigh(self, gamestate, opponent_state):
        if opponent_state.character == Character.JIGGLYPUFF:
            return True

        # Don't grab the edge if opponent is recovering high.
        #   Let's define that as: If the opponent can get onto the stage (not edge)
        #   with only a jump, without crossing the 0 Y line

        # How long will it take for opponent to reach the edge horizontally?
        frames_x = 0
        gravity = self.framedata.characterdata[opponent_state.character]["Gravity"]
        termvelocity = self.framedata.characterdata[opponent_state.character]["TerminalVelocity"]
        mobility = self.framedata.characterdata[opponent_state.character]["AirMobility"]
        airspeed = self.framedata.characterdata[opponent_state.character]["AirSpeed"]
        initialdjspeed_y = self.framedata.characterdata[opponent_state.character]["InitDJSpeed"]
        initialdjspeed_x = self.framedata.characterdata[opponent_state.character]["InitDJSpeed_x"]

        # Marth has side-b, which effectively decreases his gravity for this calculation
        if opponent_state.character == Character.MARTH:
            gravity = gravity / 2
        # Samus has bomb jumps, which gives her almost infinite horizontal recovery
        if opponent_state.character == Character.SAMUS:
            gravity = gravity / 4

        speed_x = opponent_state.speed_air_x_self + opponent_state.speed_x_attack
        speed_y = opponent_state.speed_y_self + opponent_state.speed_y_attack

        x, y = opponent_state.x, opponent_state.y

        if x > 0:
            mobility = -mobility

        # If they have a jump, assume they will use it
        if opponent_state.jumps_left > 0:
            speed_y = initialdjspeed_y
            if x > 0:
                speed_x = -initialdjspeed_x
            else:
                speed_x = initialdjspeed_x

        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]

        # Move opponent frame by frame back to the edge. Do they get past it? Or fall below?
        while abs(x) > edge_x:
            y += speed_y
            speed_y -= gravity
            speed_y = max(-termvelocity, speed_y)

            x += speed_x
            speed_x += mobility
            speed_x = max(-airspeed, speed_x)
            speed_x = min(airspeed, speed_x)

        # If they are below 0, then opponent can't recover high with a jump
        if y < 0:
            return False

        return True

    def upbheight(self, opponent_state):
        character = opponent_state.character

        if character == Character.FOX:
            # If they are in the teleport section, predict how much more they have to go
            if opponent_state.action in [Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_1_AIR]:
                c = math.sqrt(opponent_state.speed_y_self**2 + opponent_state.speed_air_x_self**2)
                height = (opponent_state.speed_y_self / c) * 81.5
                return height
            return 84.55
        if character == Character.FALCO:
            # If they are in the teleport section, predict how much more they have to go
            if opponent_state.action in [Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_1_AIR]:
                c = math.sqrt(opponent_state.speed_y_self**2 + opponent_state.speed_air_x_self**2)
                height = (opponent_state.speed_y_self / c) * 61.5
                return height
            return 62.4
        if character == Character.CPTFALCON:
            return 37.62
        if character == Character.MARTH:
            return 50.72
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            return 54.39
        if character == Character.JIGGLYPUFF:
            return 0
        if character == Character.PEACH:
            return 28.96
        if character == Character.ZELDA:
            return 70.412
        if character == Character.SHEIK:
            return 69.632
        if character == Character.SAMUS:
            return 46.1019

        # This is maybe average, in case we get here
        return 40

    def upbapexframes(self, opponent_state):
        character = opponent_state.character
        if character == Character.FOX:
            return 118
        if character == Character.FALCO:
            return 70
        if character == Character.CPTFALCON:
            return 45
        if character == Character.MARTH:
            return 23
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            return 30
        if character == Character.JIGGLYPUFF:
            return 0
        if character == Character.PEACH:
            return 34
        if character == Character.ZELDA:
            return 73
        # Sheik's up-b is dumb, and has TWO points where it can grab the edge. Ugh
        #   This just counts the first
        if character == Character.SHEIK:
            return 19
        if character == Character.SAMUS:
            return 38

        # This is maybe average, in case we get here
        return 40

    # This is the very lazy way of doing this, but "meh". Maybe I'll get around to doing it right
    def isupb(self, opponent_state):
        character = opponent_state.character
        action = opponent_state.action
        if character in [Character.FOX, Character.FALCO]:
            if action in [Action.SWORD_DANCE_3_LOW, Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_1_AIR]:
                return True
        if character == Character.CPTFALCON:
            if action in [Action.SWORD_DANCE_3_LOW]:
                return True
        if character == Character.MARTH:
            if action in [Action.SHINE_RELEASE_AIR]:
                return True
        # Just remember that he gets two of them
        if character == Character.PIKACHU:
            if action in [Action.SWORD_DANCE_4_MID, Action.SWORD_DANCE_4_LOW, Action.SWORD_DANCE_1_AIR]:
                return True
        if character == Character.JIGGLYPUFF:
            return False
        if character == Character.PEACH:
            if action in [Action.SWORD_DANCE_3_LOW_AIR, Action.PARASOL_FALLING, Action.MARTH_COUNTER]:
                return True
        if character == Character.ZELDA:
            if action in [Action.SWORD_DANCE_3_HIGH, Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW]:
                return True
        if character == Character.SHEIK:
            if action in [Action.SWORD_DANCE_1_AIR, Action.SWORD_DANCE_2_HIGH_AIR, Action.SWORD_DANCE_2_MID_AIR]:
                return True
        if character == Character.SAMUS:
            if action in [Action.SWORD_DANCE_3_LOW]:
                return True
        return False

    def snaptoedgeframes(self, gamestate, opponent_state):
        # How long will it take opponent to grab the edge?
        #   Distance to the snap point of the edge
        edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
        edgedistance = abs(opponent_state.x) - (edge_x + 15)
        # Assume opponent can move at their "max" speed
        airhorizspeed = self.framedata.characterdata[opponent_state.character]["AirSpeed"]
        edgegrabframes_x = edgedistance // airhorizspeed
        fastfallspeed = self.framedata.characterdata[opponent_state.character]["FastFallSpeed"]

        # Samus can grapple, making all the math below wrong
        if opponent_state.action == Action.SWORD_DANCE_1_AIR and opponent_state.character == Character.SAMUS:
            return 1

        # Can opponent get to the vertical snap position in time?
        #   This is the shortest possible time opponent could get into position
        edgegrabframes_y = 1000
        # Are they already in place?
        if -5 > opponent_state.y > -23:
            edgegrabframes_y = 0
        # Are they above?
        elif opponent_state.y > -5:
            edgegrabframes_y = (opponent_state.y + 5) // fastfallspeed
        # Are they below?
        elif opponent_state.y < -23:
            djapexframes = self.framedata.frames_until_dj_apex(opponent_state)
            djheight = self.framedata.dj_height(opponent_state)
            # Can they double-jump to grab the edge?
            if -5 > opponent_state.y + djheight > -23:
                edgegrabframes_y = djapexframes
            elif opponent_state.y + djheight > -5:
                # If the jump puts them too high, then we have to wait for them to fall after the jump
                fallframes = (opponent_state.y + djheight + 5) // fastfallspeed
                edgegrabframes_y = djapexframes + fallframes
            elif opponent_state.y + djheight < -23:
                # If the jump puts them too low, then they have to UP-B. How long will that take?
                upbframes = self.upbapexframes(opponent_state)
                edgegrabframes_y = upbframes
                # How many falling frames do they need?
                fallframes = (opponent_state.y + upbframes + 5) // fastfallspeed
                if fallframes > 0:
                    edgegrabframes_y += fallframes

        edgegrabframes = max(edgegrabframes_x, edgegrabframes_y)

        facinginwards = opponent_state.facing == (opponent_state.x < 0)
        firefox = opponent_state.character in [Character.FOX, Character.FALCO] and \
            opponent_state.action == Action.SWORD_DANCE_3_LOW and facinginwards
        inteleport = opponent_state.character in [Character.FOX, Character.FALCO] and \
            opponent_state.action == Action.SWORD_DANCE_4_MID


        falconupbstart = opponent_state.character == Character.CPTFALCON and \
            opponent_state.action == Action.SWORD_DANCE_3_LOW and opponent_state.action_frame <= 44
        if falconupbstart:
            edgegrabframes = max(44 - opponent_state.action_frame, 0)

        # Teleport exceptions here
        #   Some characters have "teleport" moves. Sheik, Zelda, Fox, Falco, etc...
        #   Teleport moves have a startup, then you move at a set speed at any angle
        #   In these cases, opponent COULD grab the edge much faster than in other situations
        if opponent_state.character in [Character.SHEIK, Character.ZELDA, Character.FOX, Character.FALCO, \
                Character.PIKACHU, Character.PICHU, Character.MEWTWO]:
            if opponent_state.y > 0 and opponent_state.action != Action.DEAD_FALL:
                edgegrabframes = 1
                if firefox:
                    edgegrabframes = max(15 - opponent_state.action_frame, 0)
            # If in place to grab edge,
            if (-5 > opponent_state.y > -23) and firefox:
                edgegrabframes = max(15 - opponent_state.action_frame, 0)
            # If opponent is IN the teleport phase, then it matters whether they're moving up or down
            if inteleport:
                if opponent_state.speed_y_self > 0:
                    edgegrabframes = self.framedata.frame_count(opponent_state.character, opponent_state.action) - opponent_state.action_frame
                else:
                    edgegrabframes = 0

            # Pichu and Pikachu get two teleports, so just always consider them active to grab the edge
            if opponent_state.character in [Character.PIKACHU, Character.PICHU]:
                edgegrabframes = 1
        return edgegrabframes

    def step(self, gamestate, smashbot_state, opponent_state):
        self._propagate  = (gamestate, smashbot_state, opponent_state)

        recoverhigh = self.canrecoverhigh(gamestate, opponent_state)

        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step(gamestate, smashbot_state, opponent_state)
            return

        if Dropdownshine.inrange(smashbot_state, opponent_state, self.framedata):
            self.pickchain(Chains.Dropdownshine)
            return

        if smashbot_state.action == Action.EDGE_CATCHING:
            self.pickchain(Chains.Nothing)
            return

        # How many frames will it take to get to our opponent right now?
        onedge = smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]
        opponentonedge = opponent_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]

        # Stand up if opponent attacks us
        proj_incoming = Defend.needsprojectiledefense(smashbot_state, opponent_state, gamestate) and smashbot_state.invulnerability_left <= 2

        samusgrapple = opponent_state.character == Character.SAMUS and opponent_state.action == Action.SWORD_DANCE_4_LOW and \
            -25 < opponent_state.y < 0 and smashbot_state.invulnerability_left <= 2

        hitframe = self.framedata.in_range(opponent_state, smashbot_state, gamestate.stage)
        framesleft = hitframe - opponent_state.action_frame
        if proj_incoming or samusgrapple or (hitframe != 0 and onedge and framesleft < 5 and smashbot_state.invulnerability_left < 2):
            # Unless the attack is a grab, then don't bother
            if not self.framedata.is_grab(opponent_state.character, opponent_state.action):
                if self.isupb(opponent_state):
                    #TODO: Make this a chain
                    self.chain = None
                    self.controller.press_button(Button.BUTTON_L)
                    return
                else:
                    self.chain = None
                    self.pickchain(Chains.DI, [0.5, 0.65])
                    return

        # Special exception for Fox/Falco illusion
        #   Since it is dumb and technically a projectile
        if opponent_state.character in [Character.FOX, Character.FALCO]:
            if opponent_state.action in [Action.SWORD_DANCE_2_MID]:
                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return

        # What recovery options does opponent have?
        landonstage = False
        grabedge = False
        # they have to commit to an up-b to recover
        mustupb = False
        canrecover = True

        djheight = self.framedata.dj_height(opponent_state)

        edgegrabframes = self.snaptoedgeframes(gamestate, opponent_state)

        # How heigh can they go with a jump?
        potentialheight = djheight + opponent_state.y
        if potentialheight < -23:
            mustupb = True

        # Now consider UP-B
        #   Have they already UP-B'd?
        if self.isupb(opponent_state):
            if self.upbstart == 0:
                self.upbstart = opponent_state.y
            # If they are halfway through the up-b, then subtract out what they've alrady used
            potentialheight = self.upbheight(opponent_state) + self.upbstart
        elif opponent_state.action == Action.DEAD_FALL:
            potentialheight = opponent_state.y
        else:
            potentialheight += self.upbheight(opponent_state)

        # Cpt Falcon's up-b causes him to distort his model by a crazy amount. Giving him
        #   the ability to get on the stage easier. Adjust for this
        adjustedheight = potentialheight
        if opponent_state.character == Character.CPTFALCON and self.isupb(opponent_state):
            adjustedheight += 12

        # Adjust upwards a little to have some wiggle room
        if adjustedheight > -5:
            landonstage = True
        if potentialheight > -23:
            grabedge = True
        if potentialheight < -30:
            mustupb = True
            canrecover = False

        # Split the logic into two:
        #   A) We are on the edge
        #   B) We are on the stage
        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            # If opponent can't recover, then just get onto the stage!
            if not canrecover:
                #TODO: Make this a chain
                self.chain = None
                self.controller.press_button(Button.BUTTON_L)
                return

            # Don't roll up too early for Falcon
            falconupearly = opponent_state.character == Character.CPTFALCON and \
                opponent_state.action == Action.SWORD_DANCE_3_LOW and opponent_state.action_frame <= 12

            # Roll up to edgehog
            if self.isupb(opponent_state) and not landonstage and not falconupearly:
                #TODO: Make this a chain
                self.chain = None
                self.controller.press_button(Button.BUTTON_L)
                return

            # Edgestall
            # For Fox and Falco, we have a different edgestall strategy. Only edgestall if they start a FireFox
            if opponent_state.character in [Character.FOX, Character.FALCO]:
                # Are they in the start of a firefox?
                # But make sure they can't grab the edge in the middle of it
                edgedistance = abs(opponent_state.x) - (melee.stages.EDGE_GROUND_POSITION[gamestate.stage] + 15)
                inrange = (-5 > opponent_state.y > -23) and (edgedistance < 15)
                if opponent_state.action == Action.SWORD_DANCE_3_LOW and opponent_state.action_frame <= 5 and not inrange:
                    self.pickchain(Chains.Edgestall)
                    return
            # We must be on the first frame, or else it's dangerous
            elif smashbot_state.action == Action.EDGE_HANGING and smashbot_state.action_frame == 1:
                if edgegrabframes > 29 and smashbot_state.invulnerability_left >= 29:
                    self.pickchain(Chains.Edgestall)
                    return

            #  We are in danger of being attacked!
            #   It's unsafe to be in shine range of opponent. We can't react to the attack!
            if gamestate.distance < 11.8 and opponent_state.character in [Character.FOX, Character.FALCO, Character.JIGGLYPUFF] and \
                    smashbot_state.invulnerability_left <= 1:

                # If we can, challenge their shine at the edge
                if self.difficulty >= 3 and edgegrabframes > 2:
                    self.pickchain(Chains.Dropdownshine)
                    return

                self.chain = None
                self.pickchain(Chains.DI, [0.5, 0.65])
                return
            framesleft = Punish.framesleft(opponent_state, self.framedata, smashbot_state)

            # Samus UP_B invulnerability
            samusupbinvuln = opponent_state.action in [Action.SWORD_DANCE_3_MID, Action.SWORD_DANCE_3_LOW] and \
                    opponent_state.character == Character.SAMUS and opponent_state.action_frame <= 5

            # Shine them, as long as they aren't attacking right now
            frameadvantage = framesleft > 2 or smashbot_state.invulnerability_left > 2
            if gamestate.distance < 11.8 and edgegrabframes > 2 and frameadvantage and not samusupbinvuln:
                self.pickchain(Chains.Dropdownshine)
                return

            # Illusion high
            if self.illusionhighframes(gamestate, opponent_state) <= 5:
                if smashbot_state.invulnerability_left > 7:
                    self.pickchain(Chains.Edgebair)
                    return

            if self.firefoxhighframes(gamestate, opponent_state) <= 5:
                self.pickchain(Chains.Edgebair)
                return

            # Do nothing
            self.chain = None
            self.pickchain(Chains.Nothing)
            return

        # We are on the stage
        else:
            edge_x = melee.stages.EDGE_GROUND_POSITION[gamestate.stage]
            edgedistance = abs(edge_x - abs(smashbot_state.x))

            randomgrab = False
            if random.randint(0, 20) == 0:
                randomgrab = True
            if self.difficulty == 4:
                randomgrab = True

            # Can we challenge their ledge?
            framesleft = Punish.framesleft(opponent_state, self.framedata, smashbot_state)
            if not recoverhigh and not onedge and opponent_state.invulnerability_left < 5 and edgedistance < 10:
                if randomgrab or framesleft > 10:
                    wavedash = True
                    if self.framedata.is_attack(opponent_state.character, opponent_state.action):
                        wavedash = False
                    self.pickchain(Chains.Grabedge, [wavedash])
                    return

            # Dash dance near the edge
            pivotpoint = opponent_state.x
            # Don't run off the stage though, adjust this back inwards a little if it's off
            edgebuffer = 5
            pivotpoint = min(pivotpoint, edge_x - edgebuffer)
            pivotpoint = max(pivotpoint, (-edge_x) + edgebuffer)

            self.chain = None
            self.pickchain(Chains.DashDance, [pivotpoint])
