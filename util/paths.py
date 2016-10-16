import os, pwd, shutil
import configparser

def get_dolphin_home_path():
    home_path = pwd.getpwuid(os.getuid()).pw_dir
    legacy_config_path = home_path + "/.dolphin-emu/";

    #Are we using a legacy Linux home path directory?
    if os.path.isdir(legacy_config_path):
        return legacy_config_path

    #Are we on OSX?
    osx_path = home_path + "/Library/Application Support/Dolphin/";
    if os.path.isdir(osx_path):
        return osx_path

    #Are we on a new Linux distro?
    linux_path = home_path + "/.local/share/dolphin-emu/";
    if os.path.isdir(linux_path):
        return linux_path

    print("ERROR: Are you sure Dolphin is installed? Make sure it is,\
            and then run SmashBot again.")
    sys.exit(1)
    return ""

def get_dolphin_config_path():
    home_path = pwd.getpwuid(os.getuid()).pw_dir
    legacy_config_path = home_path + "/.dolphin-emu/";

    #Are we using a legacy Linux home path directory?
    if os.path.isdir(legacy_config_path):
        return legacy_config_path

    #Are we on a new Linux distro?
    linux_path = home_path + "/.config/dolphin-emu/";
    if os.path.isdir(linux_path):
        return linux_path

    #Are we on OSX?
    osx_path = home_path + "/Library/Application Support/Dolphin/";
    if os.path.isdir(osx_path):
        return osx_path

    print("ERROR: Are you sure Dolphin is installed? Make sure it is,\
            and then run SmashBot again.")
    sys.exit(1)
    return ""

def get_dolphin_pipes_path(port):
    return get_dolphin_home_path() + "/Pipes/SmashBot" + str(port)

def get_memory_watcher_socket_path():
    return get_dolphin_home_path() + "/MemoryWatcher/MemoryWatcher"

def first_time_setup(port):
    config_path = get_dolphin_home_path()
    mem_watcher_path = config_path + "MemoryWatcher/"
    pipes_path = config_path + "Pipes/"

    #Create the MemoryWatcher directory if it doesn't already exist
    if not os.path.exists(mem_watcher_path):
        os.makedirs(mem_watcher_path)
        print("WARNING: Had to create a MemoryWatcher directory in Dolphin just now. " \
            "You may need to restart Dolphin and SmashBot in order for this to work. " \
            "(You should only see this warning once)")

    #Copy over Locations.txt
    shutil.copy("util/Locations.txt", mem_watcher_path)

    #Create the Pipes directory if it doesn't already exist
    if not os.path.exists(pipes_path):
        os.makedirs(pipes_path)
        print("WARNING: Had to create a Pipes directory in Dolphin just now. " \
            "You may need to restart Dolphin and SmashBot in order for this to work. " \
            "(You should only see this warning once)")

    pipes_path += "SmashBot" + str(port)
    if not os.path.exists(pipes_path):
        os.mkfifo(pipes_path)

def configure_controller_settings(port):
    #Read in dolphin's controller config file
    controller_config_path = get_dolphin_config_path() + "GCPadNew.ini"
    config = configparser.SafeConfigParser()
    config.read(controller_config_path)

    #Add a SmashBot standard controller config to the given port
    section = "GCPad" + str(port)
    if not config.has_section(section):
        config.add_section(section)
    config.set(section, 'Device', 'Pipe/0/SmashBot' + str(port))
    config.set(section, 'Buttons/A', 'Button A')
    config.set(section, 'Buttons/B', 'Button B')
    config.set(section, 'Buttons/X', 'Button X')
    config.set(section, 'Buttons/Y', 'Button Y')
    config.set(section, 'Buttons/Z', 'Button Z')
    config.set(section, 'Buttons/L', 'Button L')
    config.set(section, 'Buttons/R', 'Button R')
    config.set(section, 'Main Stick/Up', 'Axis MAIN Y +')
    config.set(section, 'Main Stick/Down', 'Axis MAIN Y -')
    config.set(section, 'Main Stick/Left', 'Axis MAIN X -')
    config.set(section, 'Main Stick/Right', 'Axis MAIN X +')
    config.set(section, 'Triggers/L', 'Button L')
    config.set(section, 'Triggers/R', 'Button R')
    config.set(section, 'Main Stick/Modifier', 'Shift_L')
    config.set(section, 'Main Stick/Modifier/Range', '50.000000000000000')
    config.set(section, 'D-Pad/Up', 'T')
    config.set(section, 'D-Pad/Down', 'G')
    config.set(section, 'D-Pad/Left', 'F')
    config.set(section, 'D-Pad/Right', 'H')
    config.set(section, 'Buttons/Start', 'Button START')
    config.set(section, 'Buttons/A', 'Button A')
    config.set(section, 'C-Stick/Up', 'Axis C Y +')
    config.set(section, 'C-Stick/Down', 'Axis C Y -')
    config.set(section, 'C-Stick/Left', 'Axis C X -')
    config.set(section, 'C-Stick/Right', 'Axis C X +')
    config.set(section, 'Triggers/L-Analog', 'Axis L -+')
    config.set(section, 'Triggers/R-Analog', 'Axis R -+')

    with open(controller_config_path, 'w') as configfile:
        config.write(configfile)

    #Change SmashBot's controller port to use "standard" input
    dolphinn_config_path = get_dolphin_config_path() + "Dolphin.ini"
    config = configparser.SafeConfigParser()
    config.read(dolphinn_config_path)

    #Indexed at 0. "6" means standard controller
    config.set("Core", 'SIDevice'+str(port-1), "6")

    with open(dolphinn_config_path, 'w') as dolphinfile:
        config.write(dolphinfile)
