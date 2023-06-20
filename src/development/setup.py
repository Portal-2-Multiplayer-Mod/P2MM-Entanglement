import os, platform, subprocess

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

def is_pyqt5_installed():
    try:
        pkg_resources.get_distribution('PyQt5')
        return True
    except pkg_resources.DistributionNotFound:
        return False

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("../../") # this puts us at the repos root

system = platform.system().lower()

print(system)

def ask_yes_no(question):
  while True:
    print(question + " (y/n): ")
    answer = input().lower()

    if answer in ("y", "yes"):
      return True
    elif answer in ("n", "no"):
      return False
    else:
      print("Please enter a valid response (y/n).")

def install_package(package_name):
    try:
        subprocess.check_call(['pip', 'install', package_name])
        print(f"Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Installation failed: {e}")
        return False

# general packages
general_packages = [
    "rcon==2.3.9",
    "requests",
    "qt_material"
]

if system == "linux":
    import pkg_resources

    # PYQT5
    if is_pyqt5_installed():
        print("PyQt5 is installed.")
    else:
        print_color("PyQt5 is not installed.", "red")
        print_color("Please install python pyqt5 from your distro's default repo, then simply press enter.", "yellow")
        input()
        if is_pyqt5_installed():
            print_color("PyQt5 is installed.", "green")
        else:
            if ask_yes_no("PyQt5 is still not installed... we can try to install it using pip but unless you are on a rolling distro like arch it likly wont run as the qt versions will mismatch. Would you like to install it through pip automatically?"):
                if not install_package("pyqt5"):
                    print("Error installing PyQt5. Exiting.", "red")
                    exit()
                else:
                    print("PyQt5 installed, if it causes problems or doesn't run then run 'pip uninstall pyqt5'")
            else:
                print("PyQt5 is not installed. Exiting.", "red")
                exit()

    #! linux only packages go here
    packagelist = []

    for package in general_packages:
        packagelist.append(package)
    for package in packagelist:
        try:
            pkg_resources.get_distribution(package.split("==")[0])
        except pkg_resources.DistributionNotFound:
            install_package(package)
elif system == "windows":
    #! windows only packages go here
    packagelist = [
        "win32gui",
        "pyqt5",
    ]

    for package in general_packages:
        packagelist.append(package)
    for package in packagelist:
        try:
            pkg_resources.get_distribution(package.split("==")[0])
        except pkg_resources.DistributionNotFound:
            install_package(package)