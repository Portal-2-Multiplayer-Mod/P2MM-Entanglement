#!/bin/python

#* PURPOSE: take a pre-existing portal 2 and strip it down into a dedicated
#* server-like environment that run's headlessly and without a steam account

import os, time, shutil, sys
from modules.functions import *

def buildserver(gamepath, outputpath):
    f = open("gamefiles.txt")
    filelist = f.read().strip().replace("/", os.sep).split("\n")
    f.close()

    #* create whatever paths need to exist
    if not os.path.exists(gamepath):
        print("path doesn't exist")
        exit()

    if os.path.exists(outputpath):
        shutil.rmtree(outputpath)
    os.mkdir(outputpath)

    #* assemble the base server
    print("symlinking server")
    oldtime = time.time()
    for fl in filelist:
        symlink(gamepath + fl, outputpath + fl)
    print("symlinking finished in: " + str(time.time() - oldtime) + " seconds!")
    
    #* for whatever reason steam_api.dll doesn't work with a symlinked steam.inf file so we need to copy it instead
    shutil.copy(gamepath + "portal2/steam.inf", outputpath + "portal2/steam.inf")

    #* download goldberg into the correct folder
    if not os.path.isfile("goldberg.dll"):
        print("downloading goldberg...")
        try:
            downloadgoldberg("goldberg.dll")
        except:
            print("failed to download goldberg! game will not start without a steam emulator")
            print("please manually download goldberg from https://mr_goldberg.gitlab.io/goldberg_emulator/ open the zip and extract only steam_api.dll to this folder and name it goldberg.dll")
            sys.exit(0)
        print("downloaded goldberg")
    shutil.copy("goldberg.dll", outputpath + "bin/steam_api.dll")
    os.makedirs(outputpath + "bin/steam_settings")
    f = open(outputpath + "bin/steam_settings/force_account_name.txt", "w")
    f.write("server")
    f.close()