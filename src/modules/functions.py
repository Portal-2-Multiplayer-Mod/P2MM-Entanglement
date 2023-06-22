"""
    Has common functions that we use repeatedly throughout the project
"""

import os, shutil, zipfile, platform, subprocess, socket, string, random, urllib.request
from rcon.source import Client
from modules.logging import log

rconPassword: str

Hostname: str
LocalIp: str

RconHist: list
UserRconHist: list


def __init() -> None:
    """
    Initializes local variables,
    !Called at the bottom of the file
    """
    global rconPassword, Hostname, LocalIp, RconHist, UserRconHist

    rconPassword = GenerateRandomString(6)

    Hostname = socket.gethostname()
    LocalIp = socket.gethostbyname(Hostname)

    RconHist = []
    UserRconHist = []


def GenerateRandomString(length: int) -> str:
    """Generates a random string

    Parameters
    ----------
    length : int
        length of the desired string

    Returns
    -------
    str
        a string of random lowercase letters
    """

    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def SendRcon(cmd: str, password: str, port: int = 3280, hist: bool = False) -> str:
    """Genuinely no idea what it does

    Parameters
    ----------
    cmd : str
        command to be sent
    password : str
        server password
    port : int, optional
        by default 3280
    hist : bool, optional
        no idea, by default False

    Returns
    -------
    str
        response
    """
    if hist:
        UserRconHist.reverse()
        UserRconHist.append(cmd)
        UserRconHist.reverse()
    else:
        RconHist.append(cmd)

    try:
        with Client(LocalIp, port, passwd=password) as client:
            response = client.run(cmd)
        return response
    except Exception as e:
        #! FOR THE LOVE OF GOD LOG THE EXCEPTION OR PRINT IT
        log(str(e))
        return ""


def GetSystem() -> str:
    """returns the operating system's name

    Returns
    -------
    str
        OS name
    """

    system = platform.system().lower()
    return system


def GetAllFilesInDir(directory: str) -> list[str]:
    """gets the relative path of all files under a directory

    Parameters
    ----------
    directory : str
        the directory to search in

    Returns
    -------
    list[str]
        list of files' paths relative to the directory provided
    """

    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            files_list.append(file_path)
    return files_list


def __CreateSymlink(original: str, new: str) -> None:
    """creates a symlink

    Parameters
    ----------
    original : str
        the Target file
    new : str
        path of the link
    """

    if GetSystem() == "linux":
        os.symlink(original, new)

    elif GetSystem() == "windows":
        with open("NUL", "w") as fh:
            subprocess.Popen(
                f'mklink /H "{new}" "{original}"', shell=True, stdout=fh, stderr=fh
            )


def Symlink(original: str, new: str) -> None:
    """creates a symlink, will do nothing if the original path is invalid

    Parameters
    ----------
    original : str
        the Target file
    new : str
        path of the link
    """

    if not os.path.exists(original):
        log(f"symlink failed! file '{original}' doesn't exist")
        return

    if not os.path.exists(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new))

    # * if its a directory iterate through it and symlink every file
    if os.path.isdir(original):
        for file in GetAllFilesInDir(original):
            __CreateSymlink(original + file, new + file)
        return

    __CreateSymlink(original, new)


def ReadPatchFile(filepath) -> list[list[str]]:
    data = ReadFile(filepath).strip().split("\n")
    newData: list[str] = []

    for line in data:
        line = line.strip()
        if line.startswith("//"):
            continue
        line = line.split("//")[0].strip()
        newData.append(line.lower())

    operations: list[list[str]] = []
    for line in newData:
        if line.startswith("replace:"):
            line = line.replace("replace:", "").strip()
            operation = line.split("|")
            operation[0] = bytes.fromhex(operation[0].strip().replace(" ", ""))
            operation[1] = bytes.fromhex(operation[1].strip().replace(" ", ""))
            operations.append(operation)

    return operations


def PatchData(binaryPath, patchFilePath):
    operations = ReadPatchFile(patchFilePath)

    data = ReadFile(binaryPath, "rb")

    for op in operations:
        data = data.replace(op[0], op[1])

    WriteToFile(binaryPath, data, "wb")


def DownloadFile(url:str, downloadPath:str) -> bool:
    """Downloads a file to the specified path

    Parameters
    ----------
    url : str
        the file's link
    local_filename : str
        path to download to (must include file name)

    Returns
    -------
    bool
        true if downloaded, false if failed
    """

    try:
        urllib.request.urlretrieve(url, downloadPath)
    except Exception as e:
        log(str(e), "error")
        return False

    if os.path.exists(downloadPath):
        log(f"downloaded {os.path.basename(downloadPath)} successfully")
        return True
    return False

# * we need a way to download the latest version of the goldberg emulator https://mr_goldberg.gitlab.io/
def DownloadGoldberg(outputPath: str = "steam_api.dll") -> bool:
    """simply downloads goldberg

    Parameters
    ----------
    outputPath : str, optional
        where to extract 'steam_api.dll', by default "steam_api.dll"

    Returns
    -------
    bool
        the download status, true if successful, false if failed
    """

    downloadFolder = "pydowntemp"
    downloadPath = downloadFolder + "/goldberg.zip"

    if os.path.exists(downloadFolder):
        shutil.rmtree(downloadFolder)

    os.mkdir(downloadFolder)

    isDownloaded = DownloadFile(
        "https://gitlab.com/Mr_Goldberg/goldberg_emulator/uploads/2524331e488ec6399c396cf48bbe9903/Goldberg_Lan_Steam_Emu_v0.2.5.zip",
        downloadPath,
    )

    if not isDownloaded:
        log("there was an issue downloading goldburg, please read the logs")
        return False

    with zipfile.ZipFile(downloadPath) as zip_ref:
        zip_ref.extractall(downloadFolder)

    if os.path.exists("steam_api.dll"):
        os.remove("steam_api.dll")

    shutil.copy(downloadFolder + "/steam_api.dll", outputPath)
    shutil.rmtree(downloadFolder)
    return True


def ReadFile(fileName: str, mode: str = "r", _encoding="utf-8") -> str:
    """Returns the content of a file as a string

    Parameters
    ----------
    fileName : str
        absolute path to the file
    mode : str, optional
        read mode, by default "r"
    _encoding : str, optional
        read encoding to use, by default "utf-8"

    Returns
    -------
    str
        content of the file
    """

    #* binary mode doesn't take encoding parameter
    if mode.endswith("b"):
        with open(fileName, mode) as f:
            return f.read()

    with open(fileName, mode, encoding=_encoding) as f:
        return f.read()



def WriteToFile(fileName: str, text: str, mode: str = "w", _encoding="utf-8") -> None:
    """Writes to the specified file

    Parameters
    ----------
    fileName : str
        absolute path to the file
    text : str
        text to write
    mode : str, optional
        write mode, by default "w"
    _encoding : str, optional
        write encoding to use, by default "utf-8"
    """

    #* binary mode doesn't take encoding parameter
    if mode.endswith("b"):
        with open(fileName, mode) as f:
            f.write(text)
        return

    with open(fileName, mode, encoding=_encoding) as f:
        f.write(text)


__init()
