# SmashBot
###### The AI that beats you at Melee

### FAQ

1. **What character does SmashBot play?**

    Fox, of course!

2. **It looks like there was a big code change, what's up with that?**

    This is a complete rewrite, this time in Python! The first version of SmashBot was extremely kludgey, and I knew that it was going to be impractical to extend that code to become anything more than it already was.

    This time around, SmashBot was written from the ground up to be opponent-agnostic (so that we can fight other characters than Marth) and to be generally cleaner.

    As part of that, all the low-level plumbing functions behind interfacing with Dolphin and doing Melee related lookups has been moved over to a separate project called `libmelee`. (https://github.com/altf4/libmelee) This makes it easier than ever before to make your very own Melee AI! Go check it out.

3. **Does SmashBot cheat?**

    The short answer is: No.

    The long answer is that SmashBot only interfaces with the game by pressing buttons on a virtual controller. There isn't anything it does that you **couldn't** do in principle. It just so happens, however, that a computer is much faster and more reliable than you, so it's able to do things that a human realistically can't.

4. **How is SmashBot designed?**

    SmashBot makes decisions on a tiered hierarchy of objectives: Strategies, Tactics, and Chains. Each objective inspects the current game state and decides which lower level objective will be best to achieve it.

    **Strategies** are the highest level means that the AI will use to accomplish the overall goal. For instance, the SmashBot will typically take the strategy of baiting the opponent into a poor move.

    **Tactics** are lowish level series of predictable circumstances that we can realistically flowchart our way through. For instance, if the enemy if off the stage we may choose to edge guard them to keep them from getting back on.

    **Chains** are the lowest level of objective that consists of a "chain" of button presses that Smashers will recognize, such as Wavedash, Jump-canceled Upsmash, etc...

5. **Can I play SmashBot on a regular Gamecube or hacked Wii?**

    For right now, SmashBot only runs on a PC as a normal computer program. (Meaning that Melee has to be in an emulator) But I do want to get it running on actual Gamecube/Wii hardware. If you'd like to help with this, let me know!

6. **What Operating Systems does it play on?**

    SmashBot runs on Linux/OSX currently. Under the hood, we use a named pipe input system to Dolphin, which is *nix only. If you'd like there to be Windows support, feel free to take a look at the Issues section here on Github.

7. **I found a bug. How can I help?**

    Hey thanks, that's awesome! For starters, make sure you can reliably reproduce the bug. Then go ahead and make an Issue on GitHub at https://github.com/altf4/SmashBot/issues. If you want to be even MORE awesome, run the AI with the "--debug" flag and upload the CSV file it gives you along with the issue. That CSV contains a full breakdown of the AI's state at each frame, so we can easily pinpoint what went wrong and where.


## Setup Steps:

1. Install libmelee, a Python 3 API for interacting with Dolphin and Melee. It's in pip. On most OS's, the command will look like:
`sudo pip3 install melee`.

2. Install the Dolphin version here:
https://github.com/altf4/dolphin/tree/memorywatcher-rebased
This contains an important update to allow Dolphin to be able to read projectile information from Melee. Unfortunately, you'll have to build this from source until they accept my Pull Request:
https://github.com/dolphin-emu/dolphin/pull/4407

3. Make sure you're running Melee v1.02 NTSC. Other versions will not work.

4. If you want to play interactively with or against your AI, you'll probably want a GameCube Adapter, available on Amazon here: https://www.amazon.com/Super-Smash-GameCube-Adapter-Wii-U/dp/B00L3LQ1FI

5. If you're using a GameCube Adapter, make sure to install the drivers / confugure the udev rules, as described here:
https://wiki.dolphin-emu.org/index.php?title=How_to_use_the_Official_GameCube_Controller_Adapter_for_Wii_U_in_Dolphin

6. Apply the latest `Melee Netplay Community Settings` Gecko Code. It's available by default in Dolphin 5.0. SmashBot will NOT work properly without this. (Long story) You will need to enable cheat codes in Dolphin by choosing `Config->General Tab->Enable Cheats` Then right click on the Melee game at the Dolphin home screen and go to `Properties->Gecko Codes` to find the Gecko Code list.

7. Apply `Press Y to toggle frozen stages` Gecko Code. If you want to play on Pokemon Stadium, use the frozen version.

8. Run `smashbot.py`

9. By default, SmashBot takes controller 2, and assumes you're on controller 1. You can change this with the `--port N`  option to change SmashBot's port, and `--opponent N` to change the human player's port.
