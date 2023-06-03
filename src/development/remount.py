# DEVELOPER FILE
# purpose: remount the files to the game after a change

import os,shutil

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.chdir("..")

game = ".builtserver"
files = "modfiles"

def get_all_files(directory):
    file_list = []
    for root, directories, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list.append(file_path)
    
    return file_list

for file in get_all_files(files):
    file = file.replace(files + os.sep, "")

    if not (os.path.isfile(files + os.sep + file)):
        continue
    elif file.endswith(".dll"):
        print("skipped", file)
        continue

    if os.path.exists(game + os.sep + file):
        os.remove(game + os.sep + file)
    
    if not os.path.isdir(os.path.dirname(game + os.sep + file)):
        os.makedirs(os.path.dirname(game + os.sep + file))

    shutil.copyfile(files + os.sep + file, game + os.sep + file)
    print(file)