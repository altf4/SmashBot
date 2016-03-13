#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include <pwd.h>
#include <csignal>
#include <string>
#include <time.h>

#include "Goals/KillOpponent.h"
#include "Goals/NavigateMenu.h"

#include "Util/GameState.h"
#include "Util/MemoryWatcher.h"
#include "Util/Logger.h"

bool isDebug = false;

void FirstTimeSetup()
{
    struct passwd *pw = getpwuid(getuid());
    std::string home_path = std::string(pw->pw_dir);
    std::string legacy_config_path = home_path + "/.dolphin-emu";
    std::string mem_watcher_path;
    std::string pipe_path;

    struct stat buffer;
    if(stat(legacy_config_path.c_str(), &buffer) != 0)
    {
        //If the legacy app path is not present, see if the new one is
        const char *env_XDG_DATA_HOME = std::getenv("XDG_DATA_HOME");
        if(env_XDG_DATA_HOME == NULL)
        {
            //Try $HOME/.local/share next
            std::string backup_path = home_path + "/.local/share/dolphin-emu";
            if(stat(backup_path.c_str(), &buffer) != 0)
            {
                std::cout << "ERROR: $XDG_DATA_HOME was empty and so was $HOME/.dolphin-emu and $HOME/.local/share/dolphin-emu " \
                    "Are you sure Dolphin is installed? Make sure it is, and then run SmashBot again." << std::endl;
                exit(-1);
            }
            else
            {
                mem_watcher_path = backup_path;
                mem_watcher_path += "/MemoryWatcher/";
                pipe_path = backup_path;
                pipe_path += "/Pipes/";
            }
        }
        else
        {
            mem_watcher_path = env_XDG_DATA_HOME;
            mem_watcher_path += "/MemoryWatcher/";
            pipe_path = env_XDG_DATA_HOME;
            pipe_path += "/Pipes/";
        }
    }
    else
    {
        mem_watcher_path = legacy_config_path + "/MemoryWatcher/";
        pipe_path = legacy_config_path + "/Pipes/";
    }

    //Create the MemoryWatcher directory if it doesn't already exist
    if(stat(mem_watcher_path.c_str(), &buffer) != 0)
    {
        if(mkdir(mem_watcher_path.c_str(), 0775) != 0)
        {
            std::cout << "ERROR: Could not create the directory: \"" << mem_watcher_path << "\". Dolphin seems to be installed, " \
                "But this is not working for some reason. Maybe permissions?" << std::endl;
            exit(-1);
        }
        std::cout << "WARNING: Had to create a MemoryWatcher directory in Dolphin just now. " \
            "You may need to restart Dolphin and SmashBot in order for this to work. (You should only see this warning once)" << std::endl;
    }

    std::ifstream src("Locations.txt", std::ios::in);
    std::ofstream dst(mem_watcher_path + "/Locations.txt", std::ios::out);
    dst << src.rdbuf();

    //Create the Pipes directory if it doesn't already exist
    if(stat(pipe_path.c_str(), &buffer) != 0)
    {
        if(mkdir(pipe_path.c_str(), 0775) != 0)
        {
            std::cout << "ERROR: Could not create the directory: \"" << pipe_path << "\". Dolphin seems to be installed, " \
                "But this is not working for some reason. Maybe permissions?" << std::endl;
            exit(-1);
        }
        std::cout << "WARNING: Had to create a Pipes directory in Dolphin just now. " \
            "You may need to restart Dolphin and SmashBot in order for this to work. (You should only see this warning once)" << std::endl;
    }
}

void signal_handler(int signal)
{
    std::string logpath = "Logs";
    struct stat buffer;

    Controller *controller = Controller::Instance();
    controller->emptyInput();

    if(isDebug)
    {
        Logger *logger = Logger::Instance();
        std::string logdump = logger->DumpLog();

        if(stat(logpath.c_str(), &buffer) != 0)
        {
            if(mkdir(logpath.c_str(), 0775) != 0)
            {
                std::cout << "ERROR: Could not create the directory: \"" << logpath << "\". Maybe permissions?" << std::endl;
                exit(EXIT_FAILURE);
            }
        }

        //Name the file as a timestamp
        static char name[20];
        time_t now = time(0);
        strftime(name, sizeof(name), "%Y%m%d_%H%M%S", localtime(&now));
        std::string filename = std::string(name);

        std::cout << "\nINFO: Log file written to: " << logpath + "/" + filename + ".csv" << std::endl;

        std::ofstream dst(logpath + "/" + filename + ".csv", std::ios::out);
        dst << logdump;
        dst.close();
    }

    exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[])
{
    if(argc > 1)
    {
        std::string arg = std::string(argv[1]);
        if(arg == "--debug")
        {
            isDebug = true;
        }
    }

    //Do some first-time setup
    FirstTimeSetup();

    std::signal(SIGINT, signal_handler);

    Logger *logger = Logger::Instance();
    logger->SetDebug(isDebug);
    GameState *state = GameState::Instance();

    MemoryWatcher *watcher = new MemoryWatcher();
    uint last_frame = 0;
    //Get our goal
    Goal *goal = NULL;
    MENU current_menu;

    //Main frame loop
    for(;;)
    {
        //If we get a new frame, process it. Otherwise, keep reading memory
        if(!watcher->ReadMemory())
        {
            continue;
        }

        current_menu = (MENU)state->m_memory->menu_state;

        if(state->m_memory->frame != last_frame)
        {
            if(state->m_memory->frame > last_frame+1)
            {
                std::cout << "WARNING: FRAME MISSED" << std::endl;
            }
            last_frame = state->m_memory->frame;

            //If we're in a match, play the match!
            if(state->m_memory->menu_state == IN_GAME)
            {
                if(goal == NULL )
                {
                    goal = new KillOpponent();
                }
                if(typeid(*goal) != typeid(KillOpponent))
                {
                    delete goal;
                    goal = new KillOpponent();
                }
                goal->Strategize();
            }
            //If we're in a menu, then let's navigate the menu
            else if(state->m_memory->menu_state == CHARACTER_SELECT ||
                state->m_memory->menu_state == STAGE_SELECT ||
                state->m_memory->menu_state == POSTGAME_SCORES)
            {
                if(goal == NULL )
                {
                    goal = new NavigateMenu();
                }
                if(typeid(*goal) != typeid(NavigateMenu))
                {
                    delete goal;
                    goal = new NavigateMenu();
                }
                goal->Strategize();
            }
        }
        //If the menu changed
        else if(current_menu != state->m_memory->menu_state)
        {
            last_frame = 1;
            current_menu = (MENU)state->m_memory->menu_state;
        }

        logger->SetGoal(goal);
        logger->LogFrame();
    }

    return EXIT_SUCCESS;
}
