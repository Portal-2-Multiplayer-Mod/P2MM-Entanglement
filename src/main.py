import os, time, multiprocessing, sys, signal
import modules.gui as gui
import modules.functions as functions
import modules.launcher as launcher
import modules.logging as logging
from modules.logging import log

def sigint_handler(signal, frame): #* remove lockfile on exit
            log("\n>EXIT SIGNAL RECIVED TERMINATING<\n")
            launcher.handlelockfile()
            sys.exit(0)
signal.signal(signal.SIGINT, sigint_handler)

os.chdir(os.path.abspath(os.path.dirname(__file__)))

### gui

gui.gui_main()
# launcher.launchgame()

###
