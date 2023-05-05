import os
import platform
import subprocess
import multiprocessing
import signal
import sys
import time
import psutil #!pip isntall psutil
from modules.builder import buildserver
from modules.functions import getsystem

if getsystem() == "darwin": 
    print("We currently do not support MacOS hosting, nor do we plan to. However, you can still join other P2MM servers from a mac client.")
    exit()
elif getsystem() == "windows":
    import win32gui #!pip install pywin32
    gamepath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2\\"
elif getsystem() == "linux":
    gamepath = os.path.expanduser("~/.steam/steam/steamapps/common/Portal 2/")

gamehidden = 0 # i have this varible outside of its respective function as the enumwindows fuction appears not to be able to handle global imports from local functions

bsdir = ".builtserver" + os.sep

def createlockfile(pid):
    f = open("p2mm.lock", "w")
    game = psutil.Process(pid)
    for child in game.children():
        f.write(str(child.pid) + "\n")
    f.close()

def destroylockfile():
    os.remove("p2mm.lock")

def handlelockfile(intentionalkill = False):
    if os.path.exists("p2mm.lock"):
        if not intentionalkill:
            print("found lock file possible zombie instance")
        f = open("p2mm.lock", "r")
        pids = f.read().strip().split("\n")
        f.close()
        for pid in pids:
                try:
                    psutil.Process(int(pid)).kill()
                    psutil.Process(int(pid)).wait()
                    print("cleaned up zombie instance")
                except:
                    print("zombie instance already died")
        destroylockfile()
            


def launchgame(builtserverdir, args):
    handlelockfile() # clean up any possible zombie instances
    buildserver(gamepath, "modfiles/", bsdir) # build the serverfiles

    # launch the game
    if getsystem() == "linux":
        process = subprocess.Popen('xvfb-run -a -s "-screen 0 1024x768x24" wine ' + builtserverdir + "portal2.exe " + args, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        createlockfile(process.pid)
        def sigint_handler(signal, frame): #* remove lockfile on exit
            print("\n>EXIT SIGNAL RECIVED TERMINATING<\n")
            print("destroying lockfile")
            destroylockfile()
            print("destroyed")
            print("exiting")
            sys.exit(0)
        signal.signal(signal.SIGINT, sigint_handler)
    elif getsystem() == "windows":
        process = subprocess.Popen('"' + builtserverdir + 'portal2.exe" ' + args, shell=True)
        
        print("game running press CTRL+C to terminate")

        def kill_game(pid):
            game = psutil.Process(pid)
            for child in game.children():
                child.kill()

        def sigint_handler(signal, frame):
            print("\n>EXIT SIGNAL RECIVED TERMINATING<\n")
            print("closing game")
            kill_game(process.pid)
            destroylockfile()
            print("closed")
            print("exiting")
            sys.exit(0)
        signal.signal(signal.SIGINT, sigint_handler)

        # hide the window after it opens
        def winEnumHandler( hwnd, ctx ):
            global gamehidden
            if win32gui.IsWindowVisible( hwnd ):
                    if ".builtserver" in win32gui.GetWindowText( hwnd ):
                        win32gui.ShowWindow(hwnd, False) # hide the window
                        gamehidden += 1

        # if the window is not hidden itterate through all visable windows and try to hide it
        print("waiting for windows to start so we can hide them")
        while (gamehidden < 3):
            output = win32gui.EnumWindows( winEnumHandler, None )
        print("all windows hidden")
        createlockfile(process.pid) # once the game is fully up create a lockfile to deal with zombie instances

curconsoleline = 0
def getnewconsolelines(confile):
    global curconsoleline
    if os.path.isfile(confile):
        f = open(confile, "r")
        consolelines = f.read().strip().split("\n")
        f.close()
        if len(consolelines) > curconsoleline:
            diff = len(consolelines) - curconsoleline
            newlines = consolelines[-diff:]
            curconsoleline = len(consolelines)
            return newlines
    return [] #return nothing if blank

if __name__ == "__main__":
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    #* launch code below
    args = "+echo p2mm +mp_dev_wait_for_other_player 0 +map mp_coop_lobby_3 +developer 1 -textmode -novid -nosound -nojoy -noipx -nopreload -norebuildaudio -condebug -refresh 30 -allowspectators -threads " + str(multiprocessing.cpu_count())
    launchgame(bsdir, args)
    print("launched game hooking console lines")
    while True:
        for line in getnewconsolelines(bsdir + "portal2" + os.sep + "console.log"):
            if ("error" in line.lower()) or ("failed" in line.lower()) or ("Couldn't" in line) or ("Unable to load" in line) or ("not found" in line):
                print("\u001b[31m" + line + "\u001b[0m")
            else:
                print(line)
        time.sleep(0.1)