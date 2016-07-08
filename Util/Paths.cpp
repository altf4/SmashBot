#include <pwd.h>
#include <iostream>
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>

#include "Paths.h"

std::string Paths::GetConfigPath()
{
    struct passwd *pw = getpwuid(getuid());
    std::string home_path = std::string(pw->pw_dir);
    std::cout << "home_path: " << home_path << std::endl;
    std::string legacy_config_path = home_path + "/.dolphin-emu";
    std::string mem_watcher_path;
    std::string pipe_path;

    struct stat buffer;
    if(stat(legacy_config_path.c_str(), &buffer) == 0)
    {
        return legacy_config_path;
    }

    //Are we on OSX?
    std::string osx_config_path = home_path + "/Library/Application Support/Dolphin/";
    std::cout << "osx_config_path: " << osx_config_path << std::endl;
    if(stat(osx_config_path.c_str(), &buffer) == 0)
    {
        return osx_config_path;
    }

    //If the legacy app path is not present, see if the new one is
    const char *env_XDG_DATA_HOME = std::getenv("XDG_DATA_HOME");
    if(env_XDG_DATA_HOME != NULL)
    {
        return std::string(env_XDG_DATA_HOME);
    }

    //Try $HOME/.local/share next
    std::string backup_path = home_path + "/.local/share/dolphin-emu";
    if(stat(backup_path.c_str(), &buffer) == 0)
    {
        return backup_path;
    }
    std::cout << "ERROR: $XDG_DATA_HOME was empty and so was $HOME/.dolphin-emu and $HOME/.local/share/dolphin-emu " \
        "Are you sure Dolphin is installed? Make sure it is, and then run SmashBot again." << std::endl;
    exit(-1);
    return "";
}
