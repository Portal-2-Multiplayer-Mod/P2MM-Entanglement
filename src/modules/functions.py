import os, shutil, requests, zipfile, platform, subprocess, socket
from rcon.source import Client

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

def sendrcon(cmd, password, port = 3280):
    try:
        print(password)
        with Client(local_ip, port, passwd=password) as client:
            response = client.run(cmd)
        return response
    except Exception as e:
        print(e)
        return ""

import urllib.request

def getsystem():
    system = platform.system().lower()
    return system

def list_files_recursive(directory):
    files_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.relpath(os.path.join(root, file), directory)
            files_list.append(file_path)
    return files_list

def puresymlink(original, new):
    if not os.path.exists(os.path.dirname(new)):
        os.makedirs(os.path.dirname(new))
    if getsystem() == "linux":
        os.symlink(original, new)
    elif getsystem() == "windows":
        fh = open("NUL","w")
        subprocess.Popen('mklink /H "%s" "%s"' % (new, original), shell=True, stdout = fh, stderr = fh)
        fh.close()

def get_all_files(directory):
    file_list = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(os.path.relpath(file_path, directory))
    return file_list

def symlink(original, new):
    if os.path.exists(original):
        if not os.path.exists(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new))
        
        #* if its a directory itterate through it and sylink every file
        if os.path.isdir(original):
            for file in list_files_recursive(original):
                puresymlink(original + file, new + file)
        else:
            puresymlink(original, new)
    else:
        print("symlink failed", original)

def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

#* we need a way to download the latest version of the goldberg emulator https://mr_goldberg.gitlab.io/
def downloadgoldberg(outputpath = "steam_api.dll"):
    downloadfolder = "pydowntemp"
    downloadPath = downloadfolder+"/goldberg.zip"
    
    if os.path.exists(downloadfolder):
        shutil.rmtree(downloadfolder)
        
    os.mkdir(downloadfolder)
    urllib.request.urlretrieve("https://gitlab.com/Mr_Goldberg/goldberg_emulator/-/jobs/2987292050/artifacts/download?file_type=archive", downloadPath)
    
    if os.path.exists(downloadPath):
        print("file exist")

    with zipfile.ZipFile(downloadPath, 'r') as zip_ref:
        zip_ref.extractall(downloadfolder)
        
    if os.path.exists("steam_api.dll"):
        os.remove("steam_api.dll")
        
    shutil.copy(downloadfolder+"/steam_api.dll", outputpath)
    shutil.rmtree(downloadfolder)
