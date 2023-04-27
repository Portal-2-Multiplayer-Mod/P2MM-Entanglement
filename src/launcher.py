import os
import shutil
from modules.builder import buildserver

os.chdir(os.path.abspath(os.path.dirname(__file__)))

builtserverdir = ".builtserver/"

if __name__ == "__main__":
    gamepath = os.path.expanduser("~/.steam/steam/steamapps/common/Portal 2/")
    buildserver(gamepath, builtserverdir)
    #* launch code below
    args = "+mp_dev_wait_for_other_player 0 +map mp_coop_lobby_3 -textmode"
    os.system("wine " + builtserverdir + "portal2.exe " + args)