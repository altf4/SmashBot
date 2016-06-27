#ifndef CONSTANTS_H
#define CONSTANTS_H

//TODO: maybe marth specific
#define EDGE_HANGING_Y_POSITION -23.7163639069
#define EDGE_MAGNETISM_X 14.72
#define EDGE_MAGNETISM_Y 24

//Max tipper range, measured from Marth's center
#define MARTH_FSMASH_RANGE 38.50
#define MARTH_JAB_RANGE 34

#define MARTH_UP_B_HEIGHT 48
#define MARTH_UP_B_X_DISTANCE 18

#define MARTH_RUN_SPEED 1.7775000334

//The depth of Marth at which he can't recover anymore. If he's gone down this low, he's dead
#define MARTH_LOWER_EVENT_HORIZON -98

//The depth where Marth has to UP-B to recover, jumping and/or air dodging alone isn't enough
#define MARTH_JUMP_ONLY_EVENT_HORIZON -47

//The depth where Marth cannot land on the stage anymore. He has to grab the edge
#define MARTH_RECOVER_HIGH_EVENT_HORIZON -81

#define MARTH_UPSMASH_KILL_PERCENT 88

#define FOX_SHINE_RADIUS 11.80
#define FOX_ROLL_FRAMES 35
#define FOX_DOUBLE_JUMP_HEIGHT 40.15

//This is a little conservative, actually
#define FOX_UPSMASH_RANGE 17.5
//The closest hitbox. The one that comes out on frame 7
#define FOX_UPSMASH_RANGE_NEAR 14.5
//Conservative actually. I've missed at 15.62 at the closest
#define FOX_GRAB_RANGE 13.5
//Vertical grab range
#define FOX_GRAB_RANGE_Y 6.5

//Until it turns to a run
#define FOX_DASH_FRAMES 12
#define FOX_DASH_SPEED 2.2
#define FOX_DASH_ACCELERATION .12

//How fast a character decelerates. IE: Their speed will reduce by exactly this much per frame, if sliding
#define FOX_SLIDE_COEFICIENT 0.08
#define MARTH_SLIDE_COEFICIENT 0.06

//Distance Fox slides going into a turn from dash
#define FOX_TURN_SLIDE 0.43

//How much Fox slides when Jump-cancel grabbing at max speed
#define FOX_JC_GRAB_MAX_SLIDE 14.72

//It takes this many frames to wavedash and be back in action
#define WAVEDASH_FRAMES 14

#endif
