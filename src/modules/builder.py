# * PURPOSE: take a pre-existing portal 2 and strip it down into a dedicated
# * server-like environment that run's headlessly and without a steam account

import os
import time
import shutil
import math
from modules.functions import *
from modules.logging import log
import modules.Configs as cfg


def ConvertBytesSize(bytesSize: int) -> str:
    """cute little bytes size formatter

    Parameters
    ----------
    bytesSize : int
        Size in bytes

    Returns
    -------
    str
        Human readable file size
    """

    if bytesSize == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")

    i = int(math.floor(math.log(bytesSize, 1024)))
    p = math.pow(1024, i)
    s = round(bytesSize / p, 2)
    return "%s %s" % (s, size_name[i])


def BuildServer(modFilesPath: str, outputPath: str, isSoftBuild: bool = True) -> bool:
    """Builds the local server (symlinks the files and downloads goldburg)

    Parameters
    ----------
    gamePath : str
        portal 2 path
    modFilesPath : str
        mod files path
    outputPath : str
        local server path
    isSoftBuild : bool, optional
        no idea, by default True

    Returns
    -------
    bool
        status of the build, true id successful, false if failed (check logs)
    """
    gamePath: str = cfg.GetValue(cfg.ConfigProperties.GamePath)

    if not gamePath.endswith(os.sep):
        gamePath = gamePath + os.sep

    filesList = ReadFile("gamefiles.txt").strip().replace(
        "/", os.sep).split("\n")

    # * create whatever paths need to exist
    if not os.path.exists(gamePath):
        log("path doesn't exist")

    if os.path.exists(outputPath):
        shutil.rmtree(outputPath)
    os.mkdir(outputPath)

    def patchFileRoutine(file):
        if not os.path.exists(outputPath + os.path.dirname(file)):
            os.makedirs(outputPath + os.path.dirname(file))

        if not os.path.exists(modFilesPath + file):
            shutil.copyfile(gamePath + file, outputPath + file)

        else:
            shutil.copyfile(modFilesPath + file, outputPath + file)

        PatchData(outputPath + file, modFilesPath + file + ".patch")

    # * assemble the base server
    log("symlinking server")

    oldTime = time.time()

    for file in filesList:
        if file.startswith("#"):  # if its a comment just pass it
            continue

        if file.startswith("!hc"):  # do a hard copy if the bang is present
            file = file.replace("!hc", "").strip()

            # if a patchFile is present do a hard copy on all os's and patch the file
            if os.path.exists(modFilesPath + file + ".patch"):
                patchFileRoutine(file)

            else:
                if GetSystem() == "linux":
                    # if it isn't in modFiles symlink it, if it isn't, dont, so we can symlink that later
                    if not os.path.exists(modFilesPath + file):
                        Symlink(gamePath + file, outputPath + file)
                # we only need to hard copy on windows as linux can remove the symlinks fine when the game is running
                elif GetSystem() == "windows":
                    if not os.path.exists(outputPath + os.path.dirname(file)):
                        os.makedirs(outputPath + os.path.dirname(file))
                    if not os.path.exists(modFilesPath + file):
                        shutil.copyfile(gamePath + file, outputPath + file)

        else:
            # patch anything with a patchfile
            if os.path.exists(modFilesPath + file + ".patch"):
                patchFileRoutine(file)
            if not os.path.exists(modFilesPath + file):
                Symlink(gamePath + file, outputPath + file)

    # * tack on the modfiles
    for file in GetAllFilesInDir(modFilesPath):
        #! for some reason this doesn't work without the abspath on linux
        # * because you should add a "./"
        Symlink(os.path.abspath(modFilesPath + file), outputPath + file)

    log("symlinking finished in: " + str(time.time() - oldTime) + " seconds!")

    # * download goldberg into the correct folder
    if not os.path.isfile("goldberg.dll"):
        log("downloading goldberg...")

        if not DownloadGoldberg():
            log("failed to download goldberg! mod can't start without a steam emulator")
            log("The error was dumped into the logs")
            log(
                "if you wish you can manually download goldberg from https://mr_goldberg.gitlab.io/goldberg_emulator/ \nopen the zip and extract 'steam_api.dll' to this folder and rename it goldberg.dll"
            )
            return False

    log("goldberg is downloaded")

    shutil.copyfile("goldberg.dll", outputPath + "bin/steam_api.dll")

    os.makedirs(outputPath + "bin/steam_settings")

    # todo: figure out what this is meant to be
    # f = open(outputPath + "bin/steam_settings/offline.txt", "w", encoding="utf-8")

    # Server account name
    WriteToFile(
        outputPath + "bin/steam_settings/force_account_name.txt", "Console")
    # Server account id
    WriteToFile(
        outputPath + "bin/steam_settings/force_steamid.txt", "69696969696969696"
    )

    log("server built successfully")
    return True
