import os, subprocess, multiprocessing, signal, sys, time, random, threading, psutil

from modules.functions import GetSystem
from modules.builder import BuildServer
from modules.logging import log
import modules.functions as fn

# ? why?
random.seed(time.time())

IsGameRunning: bool = False
IsRconReady: bool = False
BuiltServerPath: str = ".builtserver" + os.sep
RconPassword: str = ""
RconPort: int = 3280
P2ConsoleLogPath: str = BuiltServerPath + "portal2" + os.sep + "console.log"
CurConsoleLine: int = 0
System: str = GetSystem()

if System == "darwin":
    log(
        "We do not support MacOS, nor do we plan to. However, you can still join other P2MM servers from a mac client."
    )
    exit(0)

# todo: make the game path configurable
if System == "windows":
    # * pip install pywin32
    import win32gui

    gamePath = "d:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2"
    if not gamePath.endswith(os.sep): gamePath = gamePath + os.sep

elif System == "linux":
    gamePath = os.path.expanduser("~/.local/share/Steam/steamapps/common/Portal 2/")

def CreateLockFile(pid: int) -> None:
    global IsGameRunning

    fn.WriteToFile("p2mm.lock", f"{str(pid)}\n")

    children = ""
    game = psutil.Process(pid)

    for child in game.children():
        children += str(child.pid) + "\n"

    fn.WriteToFile("p2mm.lock", children)

    IsGameRunning = True


def DeleteLockFile() -> None:
    if os.path.exists("p2mm.lock"):
        try:
            os.remove("p2mm.lock")
        except Exception as e:
            log(e)


def HandleLockFile(intentionalKill=False) -> None:
    global IsGameRunning, IsRconReady

    if os.path.exists("p2mm.lock"):
        # ? what's the benefit of this check?
        if not intentionalKill:
            log("found lock file possible zombie instance")

        pids = fn.ReadFile("p2mm.lock").strip().split("\n")

        # todo: we can probably use 'psutil.wait_procs()' instead
        for pid in pids:
            try:
                psutil.Process(int(pid)).kill()
                psutil.Process(int(pid)).wait()

                log("cleaned up zombie instance")
            except:
                log("zombie instance already dead")

        DeleteLockFile()

    IsGameRunning = False
    IsRconReady = False


class RconTestThread(threading.Thread):
    def run(self):
        global IsGameRunning, IsRconReady, RconPassword, RconPort

        shouldRun = True

        while shouldRun and IsGameRunning:
            try:
                # ? why are we passing the port if it's the same as the default?
                output = fn.SendRcon('script printl("ready")', RconPassword, RconPort)

                if output.strip() == "ready":
                    log("rcon ready")
                    IsRconReady = True
                    shouldRun = False

            except Exception as e:
                log(str(e), "error")
                IsRconReady = False


class WindowHideThread(threading.Thread):
    def run(self):
        global IsGameRunning

        def winEnumHandler(hwnd: int, ctx):
            if win32gui.IsWindowVisible(hwnd):
                if ".builtserver" in win32gui.GetWindowText(hwnd):
                    win32gui.ShowWindow(hwnd, False)  # hide the window

        while not IsGameRunning:
            time.sleep(0.1)

        log("game is running, trying to hide windows")

        while IsGameRunning:
            # ? why do we need the 'output'?
            output = win32gui.EnumWindows(winEnumHandler, None)
            time.sleep(0.1)


def LaunchGame(
    builtServerDir: str = BuiltServerPath,
    rconLocalPassword: str = None,
    launchArgs: str = None,
) -> subprocess.Popen[bytes] | None:
    """Starts portal 2

    Parameters
    ----------
    builtServerDir : str, optional
        the location where to build the local server, by default BuiltServerPath

    rconLocalPassword : str, optional
        the server's password, by default generates a random string

    launchArgs : str, optional
        args to use when starting portal 2, if nothing provided the default args will be used

    Returns
    -------
    subprocess.Popen[bytes]
        the game's process
    """
    global RconPassword, IsRconReady

    IsRconReady = False

    if rconLocalPassword == None:
        rconLocalPassword = fn.GenerateRandomString(8)
    RconPassword = rconLocalPassword

    if launchArgs == None:
        launchArgs = f"+hostname P2MM +sv_client_min_interp_ratio 0 +sv_client_max_interp_ratio 1000 +mp_dev_wait_for_other_player 0 +developer 1 +map mp_coop_lobby_3 -usercon -textmode -novid -nosound -nojoy -noipx -norebuildaudio -condebug -refresh 30 -allowspectators -threads {str(multiprocessing.cpu_count())} +port 3280"
    # ? does the rcon password need to be at the start?
    launchArgs = f"+rcon_password {RconPassword} {launchArgs}"

    # clean up any possible zombie instances
    HandleLockFile()

    if not BuildServer(gamePath, "modfiles/", builtServerDir):
        return

    # launch the game
    if System == "linux":
        log("Running In linux mode!")

        def CreateWinePrefix(folderPath: str) -> bool:
            if os.path.exists(folderPath):
                log("The Wine prefix folder already exists.")

            else:
                try:
                    os.makedirs(folderPath)
                    log("Wine prefix folder created successfully.")

                except Exception as e:
                    log("Failed to create Wine prefix folder.")
                    log(str(e), "error")
                    return False
            return True

        if not CreateWinePrefix("p2mmwinepfx"):
            return

        os.environ["WINEPREFIX"] = os.path.abspath("p2mmwinepfx")
        process = subprocess.Popen(
            f'wine "{builtServerDir}portal2.exe" {launchArgs}', shell=True
        )

        while not os.path.isfile(P2ConsoleLogPath):
            time.sleep(0.1)

        log(str(process.pid) + "=============================")
        CreateLockFile(process.pid)

    elif System == "windows":
        process = subprocess.Popen(
            f'"{builtServerDir}portal2.exe" ' + launchArgs, shell=True
        )

        log("game is running press CTRL+C to terminate")

        def KillGame(pid: int):
            game = psutil.Process(pid)
            for child in game.children():
                # i love coding keywords
                child.kill()

        def sigint_handler(signal, frame):
            log("\n>EXIT SIGNAL RECEIVED TERMINATING<\n")
            log("closing game")
            KillGame(process.pid)
            DeleteLockFile()
            log("closed")
            log("exiting")
            sys.exit(0)

        try:
            signal.signal(signal.SIGINT, sigint_handler)
        except Exception as e:
            print(str(e))
            pass

        # hide the window after it opens

        # if the window is not hidden iterate through all visible windows and try to hide it
        log("waiting for game to start so we can hide and lock it")

        hideWindowThread = WindowHideThread()
        hideWindowThread.daemon = True
        hideWindowThread.start()

        while not os.path.isfile(P2ConsoleLogPath):
            time.sleep(0.1)

        # once the game is fully up create a lockfile to deal with zombie instances
        CreateLockFile(process.pid)
        log("all windows hidden and game locked")

    rconTestThread = RconTestThread()
    rconTestThread.daemon = True
    rconTestThread.start()
    return process


def GetNewConsoleLines(consoleFile: str) -> list[str]:
    """gets the latest console lines from portal 2

    Parameters
    ----------
    consoleFile : str
        the path of the console logs' file

    Returns
    -------
    list[str]
        the new lines (empty list if there're none)
    """

    global CurConsoleLine

    if os.path.isfile(consoleFile):
        consoleLines = fn.ReadFile(consoleFile, _encoding="latin-1").strip().split("\n")

        if len(consoleLines) > CurConsoleLine:
            diff = len(consoleLines) - CurConsoleLine
            newlines = consoleLines[-diff:]
            CurConsoleLine = len(consoleLines)
            return newlines

    return []


if __name__ == "__main__":
    # todo: FOR THE LOVE OF GOD STOP USING CHDIR
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    # * launch code below
    LaunchGame(BuiltServerPath)

    log("game started, hooking console lines")

    while True:
        for line in GetNewConsoleLines(
            BuiltServerPath + "portal2" + os.sep + "console.log"
        ):
            log(line, "game")
        time.sleep(0.1)
