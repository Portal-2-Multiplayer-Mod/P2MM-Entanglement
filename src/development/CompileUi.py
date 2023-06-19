
#! DEVELOPER FILE
#! purpose: compile the UI file into a python's file

import os, subprocess

# get path of the "src" folder
srcPath = os.path.dirname(os.path.dirname(__file__))+ os.sep

# compile the ui file
output = subprocess.getoutput(f"python -m PyQt5.uic.pyuic -x {srcPath}main.ui -o {srcPath}modules" + os.sep + "exportedui.py")

# if the compilation was successful "output" will be empty
print(output)
