import os
import platform
import subprocess
import multiprocessing
import signal
import sys
import win32gui #pip install pywin32
import psutil #pip isntall psutil
from modules.builder import buildserver

system = platform.system().lower()
linux = "linux"
windows = "windows"

if system == "darwin": 
    print("We currently do not support MacOS hosting, nor do we plan to. However, you can still join other P2MM servers from a mac client.")
    exit()
elif system == windows:
    gamepath = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Portal 2\\"
elif system == linux:
    gamepath = os.path.expanduser("~/.steam/steam/steamapps/common/Portal 2/")

os.chdir(os.path.abspath(os.path.dirname(__file__)))

builtserverdir = ".builtserver" + os.sep

if __name__ == "__main__":
    buildserver(gamepath, builtserverdir)
    #* launch code below
    args = "+echo p2mm +mp_dev_wait_for_other_player 0 +map mp_coop_lobby_3 +developer 1 -textmode -novid -nosound -nojoy -noipx -nopreload -norebuildaudio -condebug -refresh 30 -allowspectators -threads " + str(multiprocessing.cpu_count())

    if system == linux:
        os.system("wine " + builtserverdir + "portal2.exe " + args)
    elif system == windows:
        process = subprocess.Popen('"' + builtserverdir + 'portal2.exe" ' + args, shell=True)
        print("game running press CTRL+C to terminate")

        def kill_game():
            game = psutil.Process(process.pid)
            for child in game.children():
                child.kill()

        def sigint_handler(signal, frame):
            print("\n>EXIT SIGNAL RECIVED TERMINATING<\n")
            print("closing game")
            kill_game()
            print("closed")
            print("exiting")
            sys.exit(0)
        signal.signal(signal.SIGINT, sigint_handler)

        # hide the window after it opens
        hidden = False
        def winEnumHandler( hwnd, ctx ):
            if win32gui.IsWindowVisible( hwnd ):
                if ".builtserver" in win32gui.GetWindowText( hwnd ):
                    win32gui.ShowWindow(hwnd, False) # hide the window
                    hidden = True

        # if the window is not hidden itterate through all visable windows and try to hide it
        while not hidden:
            win32gui.EnumWindows( winEnumHandler, None )

        