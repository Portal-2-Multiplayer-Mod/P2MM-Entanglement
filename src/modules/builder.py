#!/bin/python

#* PURPOSE: take a pre-existing portal 2 and strip it down into a dedicated
#* server-like environment that run's headlessly and without a steam account

import os, time, shutil, sys
from modules.functions import *
import math
from modules.logging import log

def convert_size(size_bytes): # cute little bytes size formatter
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def buildserver(gamepath, modfilespath, outputpath, softbuild = True):
    f = open("gamefiles.txt")
    filelist = f.read().strip().replace("/", os.sep).split("\n")
    f.close()

    #* create whatever paths need to exist
    if not os.path.exists(gamepath):
        log("path doesn't exist")
        exit()

    if os.path.exists(outputpath):
        shutil.rmtree(outputpath)
    os.mkdir(outputpath)

    sizetracker = 0

    #* assemble the base server
    log("symlinking server")
    oldtime = time.time()
    for fl in filelist:
        if fl.startswith("#"): # if its a comment just pass it
            continue
        if fl.startswith("!hc"): # do a hard copy if the bang is present
            fl = fl.replace("!hc", "").strip()
            if getsystem() == "linux":
                if not os.path.exists(modfilespath + fl):
                    symlink(gamepath + fl, outputpath + fl)
            elif getsystem() == "windows": # we only need to hard copy on windows as linux can remove the symlinks fine when the game is running
                if not os.path.exists(outputpath + os.path.dirname(fl)):
                    os.makedirs(outputpath + os.path.dirname(fl))
                if not os.path.exists(modfilespath + fl):
                    sizetracker += os.path.getsize(gamepath + fl)
                    shutil.copyfile(gamepath + fl, outputpath + fl)
        else:
            if not os.path.exists(modfilespath + fl):
                symlink(gamepath + fl, outputpath + fl)

    #* tack on the modfiles
    for fl in get_all_files(modfilespath):
       symlink(os.path.abspath(modfilespath + fl), outputpath + fl) #! for some reason this doesn't work without the abspath on linux

    log("symlinking finished in: " + str(time.time() - oldtime) + " seconds!")
    
    #* download goldberg into the correct folder
    if not os.path.isfile("goldberg.dll"):
        log("downloading goldberg...")
        try:
            downloadgoldberg("goldberg.dll")
        except:
            log("failed to download goldberg! game will not start without a steam emulator")
            log("please manually download goldberg from https://mr_goldberg.gitlab.io/goldberg_emulator/ open the zip and extract only steam_api.dll to this folder and name it goldberg.dll")
            sys.exit(0)
        log("downloaded goldberg")
    shutil.copyfile("goldberg.dll", outputpath + "bin/steam_api.dll")
    sizetracker += os.path.getsize("goldberg.dll")

    os.makedirs(outputpath + "bin/steam_settings")
    f = open(outputpath + "bin/steam_settings/force_account_name.txt", "w", encoding="utf-8")
    f.write("Console") # NAME FOR SERVER ACCOUNT
    f.close()

    f = open(outputpath + "bin/steam_settings/offline.txt", "w", encoding="utf-8")
    f.close()

    f = open(outputpath + "bin/steam_settings/force_steamid.txt", "w", encoding="utf-8")
    f.write("69696969696969696") # NAME FOR SERVER ACCOUNT
    f.close()
    

    log("Final Size: " + convert_size(sizetracker))