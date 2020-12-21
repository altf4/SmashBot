#!/usr/bin/python3
import unittest
import sys
import melee

# First argument
DOLPHIN_PATH = "path"
# Second argument
ISO_PATH = "another_path"

class DolphinTest(unittest.TestCase):
    """
    Test cases that cannot be run automatically in the Github cloud environment
    Involves running Dolphin and Melee
    """

    def test_character_select(self):
        """
        Start up the console and select our charcter then quit
        """
        console = melee.Console(path=DOLPHIN_PATH, slippi_port=12345)
        controller = melee.Controller(console=console,
                                      port=1,
                                      type=melee.ControllerType.STANDARD)
        console.run(iso_path=ISO_PATH)
        self.assertTrue(console.connect())
        self.assertTrue(controller.connect())

        first_frame = True
        while True:
            gamestate = console.step()
            if first_frame:
                self.assertEqual(gamestate.frame, 0)
                first_frame = False

            if gamestate.menu_state == melee.enums.Menu.IN_GAME:
                pass
            else:
                melee.MenuHelper.menu_helper_simple(gamestate,
                                                    controller,
                                                    melee.Character.FOX,
                                                    melee.Stage.BATTLEFIELD,
                                                    "",
                                                    costume=1,
                                                    autostart=False,
                                                    swag=False)
                if gamestate.menu_state == melee.enums.Menu.CHARACTER_SELECT and (gamestate.frame > 50):
                    self.assertEqual(gamestate.players[1].character_selected, melee.Character.FOX)
                    break
        console.stop()

    def test_two_controllers_in_game(self):
        """
        Two controllers, get into game then quit
        """
        console = melee.Console(path=DOLPHIN_PATH, slippi_port=23456)
        controller_one = melee.Controller(console=console,
                                      port=1,
                                      type=melee.ControllerType.STANDARD)
        controller_two = melee.Controller(console=console,
                                      port=2,
                                      type=melee.ControllerType.STANDARD)

        console.run(iso_path=ISO_PATH)
        self.assertTrue(console.connect())
        self.assertTrue(controller_one.connect())
        self.assertTrue(controller_two.connect())

        first_frame = True
        while True:
            gamestate = console.step()
            if first_frame:
                self.assertEqual(gamestate.frame, 0)
                first_frame = False

            if gamestate.menu_state == melee.enums.Menu.IN_GAME:
                self.assertEqual(gamestate.players[1].character, melee.Character.FOX)
                self.assertEqual(gamestate.players[2].character, melee.Character.MARTH)
                break
            else:
                melee.MenuHelper.menu_helper_simple(gamestate,
                                                    controller_one,
                                                    melee.Character.FOX,
                                                    melee.Stage.BATTLEFIELD,
                                                    "",
                                                    costume=1,
                                                    autostart=True,
                                                    swag=False)
                melee.MenuHelper.menu_helper_simple(gamestate,
                                                    controller_two,
                                                    melee.Character.MARTH,
                                                    melee.Stage.BATTLEFIELD,
                                                    "",
                                                    costume=1,
                                                    autostart=False,
                                                    swag=False)
        console.stop()

if __name__ == '__main__':
    assert(len(sys.argv) == 3)
    ISO_PATH = sys.argv.pop()
    DOLPHIN_PATH = sys.argv.pop()
    unittest.main()
