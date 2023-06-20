
#! this script is for preparing the development environment
#! Note: this script assumes that you have python in PATH
#! Note: this script assumes that you're running it from the root directory of the project (python ./src/development/SetupV2.py)
#! Note: this script doesn't work on all linux distributions

import os, platform, subprocess
import pkg_resources

system = ""

# def IsAdmin():
#     try:
#         return ctypes.windll.shell32.IsUserAnAdmin()
#     except:
#         return False

def print_color(text, color):
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    if color in colors:
        print(f"{colors[color]}{text}{colors['reset']}")
    else:
        print(text)

def IsPackageInstalled(package : str) -> bool:
    try:
        pkg_resources.get_distribution(package)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def AskUser(question) -> bool:
    while True:
        print(question + " (y/n): ")
        answer = input().lower()

        if answer in ("y", "yes"):
            return True

        if answer in ("n", "no"):
            return False

        print_color("Please enter a valid response!", "red")

def CreateVenv() -> None:

    # # we need admin to activate the venv so we ask for it from the start
    # if not IsAdmin():
    #     x = ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    #     if x == 42:
    #         exit(0)
    #     else:
    #         print_color("Couldn't get admin privilege, skipping the venv part", "red")
    #         return

    #* create the venv
    try:
        subprocess.check_call("python -m venv env")
        print_color("venv created successfully", "green")

    except subprocess.CalledProcessError as e:
        print_color("an error occurred while trying to create venv!", "red")
        if not AskUser("would you like to proceed without venv (y) or quit (n)?"):
            exit(1)

    # #* set script permission to process only
    # try:
    # # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
    #     subprocess.check_call(["powershell.exe", "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"])
    #     print_color("policy set successfully", "green")

    # except subprocess.CalledProcessError as e:
    #     print_color("an error occurred while trying to allow script activation!", "red")
    #     if not AskUser("would you like to proceed without venv2 (y) or quit (n)?"):
    #         exit(1)

def InstallPackages():
    print_color("Attempting to install packages...", "blue")

    isVenvAvailable = AskUser("Would you like to create a virtual environment? (recommended)")
    if isVenvAvailable:
        CreateVenv()

    if isVenvAvailable:
        if system == "windows":
            pipPath = os.getcwd() + "\\env\\Scripts\\pip.exe"
        if system == "linux":
            pipPath = os.getcwd() + "/env/bin/pip"

    else:
        pipPath = "python -m pip"

    try:
        subprocess.check_call(pipPath+" install -r requirements.txt")
        print_color("requirements installed properly", "green")
    except subprocess.CalledProcessError as e:
        print_color("an error occurred while trying to install libs!", "red")
        exit(69)

    if isVenvAvailable:
        print_color("if you don't know how to activate venv then please read this: \nhttps://stackoverflow.com/a/76517522/12429279", "blue")

if __name__ == "__main__":

    system = platform.system().lower()

    print(system)
    print(os.getcwd())

    if system == "windows":
        InstallPackages()

    if system == "linux":
        print("you're on linux, this script may not work properly on some distros")

        if not AskUser("Would you like to proceed?"):
            exit(0)

        # PYQT5
        if not IsPackageInstalled("pyqt5"):
            print_color("PyQt5 is not installed.", "red")
            print_color("It's recommended that you install pyqt5 manually from your distro's repo", "yellow")
            if not AskUser("Would you still want the script to try installing it?"):
                exit(0)

        InstallPackages()
