#!/bin/python

#* PURPOSE: take a pre-existing portal 2 and strip it down into a dedicated
#* server-like environment that run's headlessly and without a steam account

import os
from modules.functions import *

def buildserver(gamepath, outputpath):
    f = open("gamefiles.txt")
    filelist = f.read().strip().split("\n")
    f.close()

    #* create whatever paths need to exist
    if os.path.exists(gamepath):
        print(gamepath)
    else:
        print("path doesn't exist")
        exit()

    if os.path.exists(outputpath):
        print(outputpath)
    else:
        os.mkdir(outputpath)

    #* assemble the base server
    for fl in filelist:
        symlink(gamepath + fl, outputpath + fl)

    #* for whatever reason steam_api.dll doesn't work with a symlinked steam.inf file so we need to copy it instead
    shutil.copy(gamepath + "portal2/steam.inf", outputpath + "portal2/steam.inf")

    #* download goldberg into the correct folder
    print("Downloading Goldberg...")
    downloadgoldberg(outputpath + "bin/steam_api.dll")