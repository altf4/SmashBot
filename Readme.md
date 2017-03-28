#SmashBot

##Malevolent Smash Bros: Melee AI

SmashBot is an AI that plays Super Smash Bros: Melee inside the Dolphin emulator. It has a neural network brain to outsmart and destroy humans.

## Setup Instructions

Linux / OSX only. (Windows coming soon)

1. Install the Dolphin version here:
https://github.com/altf4/dolphin/tree/memorywatcher
This contains an important update to allow Dolphin to be able to read projectile information from Melee. Unfortunately, you'll have to build this from source until they accept my Pull Request:
https://github.com/dolphin-emu/dolphin/pull/4407

2. Make sure you're running Melee v1.02 NTSC. Other versions will not work.

3. If you want to play interactively with or against SmashBot, you'll probably want a GameCube Adapter, available on Amazon here: https://www.amazon.com/Super-Smash-GameCube-Adapter-Wii-U/dp/B00L3LQ1FI

4. Run `./smashbot.py`
