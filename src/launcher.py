import os
import shutil
from modules.builder import buildserver

os.chdir(os.path.abspath(os.path.dirname(__file__)))

builtserverdir = ".builtserver/"

if __name__ == "__main__":
    gamepath = os.path.expanduser("~/.steam/steam/steamapps/common/Portal 2/")
    if os.path.exists(builtserverdir):
        shutil.rmtree(builtserverdir)
    buildserver(gamepath, builtserverdir)