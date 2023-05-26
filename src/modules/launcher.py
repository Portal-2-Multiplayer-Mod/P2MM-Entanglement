from collections.abc import Callable, Iterable, Mapping
import os
import platform
import subprocess
import multiprocessing
import signal
import sys
import time
import random
import string
import threading
from typing import Any

import psutil #!pip isntall psutil
from modules.builder import buildserver
from modules.functions import getsystem
import modules.functions as functions
from modules.logging import log

random.seed(time.time())

gameisrunning = False
RconReady = False

if getsystem() == "darwin": 
    log("We currently do not support MacOS hosting, nor do we plan to. However, you can still join other P2MM servers from a mac client.")
    exit()
elif getsystem() == "windows":
    import win32gui #!pip install pywin32
    gamepath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2\\"
elif getsystem() == "linux":
    gamepath = os.path.expanduser("~/.local/share/Steam/steamapps/common/Portal 2/")

gamehidden = 0 # i have this varible outside of its respective function as the enumwindows fuction appears not to be able to handle global imports from local functions

bsdir = ".builtserver" + os.sep

def createlockfile(pid):
    global gameisrunning
    f = open("p2mm.lock", "w", encoding="utf-8")
    game = psutil.Process(pid)
    for child in game.children():
        f.write(str(child.pid) + "\n")
    f.close()
    gameisrunning = True

def destroylockfile():
    if os.path.exists("p2mm.lock"):
        os.remove("p2mm.lock")

def handlelockfile(intentionalkill = False):
    global gameisrunning
    global RconReady

    if os.path.exists("p2mm.lock"):
        if not intentionalkill:
            log("found lock file possible zombie instance")
        f = open("p2mm.lock", "r", encoding="utf-8")
        pids = f.read().strip().split("\n")
        f.close()
        for pid in pids:
                try:
                    psutil.Process(int(pid)).kill()
                    psutil.Process(int(pid)).wait()
                    log("cleaned up zombie instance")
                except:
                    log("zombie instance already died")
        destroylockfile()
    gameisrunning = False
    RconReady = False

def randomword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

class RconTestThread(threading.Thread):     
    def run(self):
        global gameisrunning
        global RconReady
        global rconpasswd, rconport
        shouldrun = True
        while shouldrun and gameisrunning:
            try:
                print("testing rcon")
                output = functions.sendrcon('script printl("ready")', rconpasswd, rconport)
                if output.strip() == "ready":
                    print("READY")
                    print("rcon passed!!!!!!!!!!!!!!")
                    RconReady = True
                    shouldrun = False
            except:
                print("rcon failed")
                RconReady = False

rconpasswd = ""
rconport = 3280
def launchgame(builtserverdir = bsdir, rconpasswdlocal="blank", launchargs="+hostname P2MM +sv_client_min_interp_ratio 0 +sv_client_max_interp_ratio 1000 +mp_dev_wait_for_other_player 0 +developer 1 +map mp_coop_lobby_3 -usercon -textmode -novid -nosound -nojoy -noipx -norebuildaudio -condebug -refresh 30 -allowspectators -threads " + str(multiprocessing.cpu_count()) + " +port 3280"):
    global rconpasswd
    global RconReady
    RconReady = False
    if rconpasswdlocal != "blank":
        rconpasswd = rconpasswdlocal
    else:
        rconpasswd = randomword(8)

    handlelockfile() # clean up any possible zombie instances

    buildserver(gamepath, "modfiles/", bsdir) # build the serverfiles
    log("buildserver routine finished!")
    launchargs = "+rcon_password " + rconpasswd + " " + launchargs

    # launch the game
    if getsystem() == "linux":
        log("Running In linux mode!")
        process = subprocess.Popen('xvfb-run -a -s "-screen 0 1024x768x24" wine ' + builtserverdir + "portal2.exe " + launchargs, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        createlockfile(process.pid)
        log("Game Died!!")
    elif getsystem() == "windows":
        process = subprocess.Popen('"' + builtserverdir + 'portal2.exe" ' + launchargs, shell=True)
        
        log("game running press CTRL+C to terminate")

        def kill_game(pid):
            game = psutil.Process(pid)
            for child in game.children():
                child.kill()
        
        def sigint_handler(signal, frame):
            log("\n>EXIT SIGNAL RECIVED TERMINATING<\n")
            log("closing game")
            kill_game(process.pid)
            destroylockfile()
            log("closed")
            log("exiting")
            sys.exit(0)
        try:
            signal.signal(signal.SIGINT, sigint_handler)
        except:
            pass

        # hide the window after it opens
        def winEnumHandler( hwnd, ctx ):
            global gamehidden
            if win32gui.IsWindowVisible( hwnd ):
                    if ".builtserver" in win32gui.GetWindowText( hwnd ):
                        win32gui.ShowWindow(hwnd, False) # hide the window
                        gamehidden += 1

        # if the window is not hidden itterate through all visable windows and try to hide it
        log("waiting for windows to start so we can hide them")
        while (gamehidden < 3):
            output = win32gui.EnumWindows( winEnumHandler, None )
        log("all windows hidden")
        createlockfile(process.pid) # once the game is fully up create a lockfile to deal with zombie instances

        rcontestthread = RconTestThread()
        rcontestthread.daemon = True
        rcontestthread.start()
    return process

curconsoleline = 0
def getnewconsolelines(confile):
    global curconsoleline
    if os.path.isfile(confile):
        f = open(confile, "r", encoding="utf-8")
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
    launchgame(bsdir)
    log("launched game hooking console lines")
    while True:
        for line in getnewconsolelines(bsdir + "portal2" + os.sep + "console.log"):
                log(line, "game")
        time.sleep(0.1)
