#SmashBot

##The AI that beats you at Melee

SmashBot is an AI that plays Super Smash Bros: Melee inside the Dolphin emulator. The goal is to make an AI that human beings cannot defeat.

##Sample Features

###Frame-Perfect Powershielding
![Powershield](images/Powershield.gif)

###Punishes Laggy Moves
![Powershield](images/RollPunish.gif)

###Flowcharted Edgeguarding
![RollPunish](images/MarthKiller.gif)

###Short-Hop Double Laser
![RollPunish](images/SHDL.gif)

###Plus way more!

###FAQ

1. **What character does SmashBot play?**

    Fox, of course!

2. **Does SmashBot cheat?**

    The short answer is: No.

    The long answer is that SmashBot only interfaces with the game by pressing buttons on a virtual controller. There isn't anything it does that you **couldn't** do in principle. It just so happens, however, that a computer is much faster and more reliable than you, so it's able to do things that a human realistically can't.

3. **Are there any current limitations to SmashBot?**

    Yes, right now SmashBot is limited to playing against Marth only, and on Final Destination. Support for other characters and stages will be added soon.

4. **How is SmashBot designed?**

    SmashBot makes decisions on a 4 tiered hierarchy of objectives: Goals, Strategies, Tactics, and Chains. Each objective inspects the current game state and decides which lower level objective will be best to achieve it.

    **Goals** are the highest level objective, and inform the AI what the intended overall outcome should be. IE: Beating our opponent in a match, or navigating the menu to select our character.

    **Strategies** are the highest level means that the AI will use to accomplish the overall goal. For instance, the SmashBot will typically take the strategy of baiting the opponent into a poor move.

    **Tactics** are lowish level series of predictable circumstances that we can realistically flowchart our way through. For instance, if the enemy if off the stage we may choose to edge guard them to keep them from getting back on.

    **Chains** are the lowest level of objective that consists of a "chain" of button presses that Smashers will recognize, such as Wavedash, Jump-canceled Upsmash, etc...

5. **Can I play SmashBot on a regular Gamecube or hacked Wii?**

    For right now, SmashBot only runs on a PC as a normal computer program. (Meaning that Melee has to be in an emulator) But I do want to get it running on actual Gamecube/Wii hardware. If you'd like to help with this, let me know!

6. **What Operating Systems does it play on?**

    SmashBot runs on Linux currently. Under the hood, we use a named pipe input system to Dolphin, which is *nix only. There are no plans to make a Windows port. If we're going to spend time porting, it's going to be to a Gamecube/Wii.

7. **I found a bug. How can I help?**

    Hey thanks, that's awesome! For starters, make sure you can reliably reproduce the bug. Then go ahead and make an Issue on GitHub at https://github.com/altf4/SmashBot/issues. If you want to be even MORE awesome, run the AI with the "--debug" flag and upload the CSV file it gives you along with the issue. That CSV contains a full breakdown of the AI's state at each frame, so we can easily pinpoint what went wrong and where.


##Rough Setup Steps:

###Works on: Ubuntu 15.04+

1. Get a working build of dolphin from source. The latest master branch should be fine. You can find it here:
https://github.com/dolphin-emu/dolphin
2. Configure your controller settings for player 1 and player 2. You will play as Player 1, SmashBot will take Player 2. You'll probably want a GameCube controller adapter. Configuring controller settings is out of the scope of this document, but check out the file `GCPadNew.ini` provided here for an example controller config that ought to work. Just stick that in your Dolphin config directory.
3. Build SmashBot code by just running make. `make` There shouldn't be any dependencies to download. (Other than Dolphin)
4. Run `./smashbot`
5. Run dolphin and start up Melee.
6. Move focus over to the dolphin window. (Or else turn on background input on the controller) Just click on the dolphin window to do this.
7. Set player 1 to Marth. SmashBot will choose its own character.  Set the stage to Final Destination. Start the match.
