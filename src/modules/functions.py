import os, shutil, requests, zipfile

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
    os.symlink(original, new)

def symlink(original, new):
    if os.path.exists(original):
        if not os.path.exists(os.path.dirname(new)):
            os.makedirs(os.path.dirname(new))
        
        #* if its a directory itterate through it and sylink every file
        if os.path.isdir(original):
            for file in list_files_recursive(original):
                puresymlink(original + file, new + file)
                print('"' + new.replace(".builtserver/", "") + file + '",')
        else:
            os.symlink(original, new)
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
def downloadgoldberg():
    page = requests.get("https://mr_goldberg.gitlab.io/goldberg_emulator/")
    for elm in str(page.content).split('href="'):
        if elm.startswith("https://gitlab.com/Mr_Goldberg/goldberg_emulator/-/jobs/"):
            elm = elm.split('"')[0]
            break
    if os.path.exists("pydowntemp"):
        shutil.rmtree("pydowntemp")
    os.mkdir("pydowntemp")
    download_file(elm, "pydowntemp/goldberg.zip")
    with zipfile.ZipFile("pydowntemp/goldberg.zip", 'r') as zip_ref:
        zip_ref.extractall("pydowntemp")
    shutil.copy("pydowntemp/steam_api.dll", "steam_api.dll")
    shutil.rmtree("pydowntemp")

if __name__ == "__main__":
    downloadgoldberg()