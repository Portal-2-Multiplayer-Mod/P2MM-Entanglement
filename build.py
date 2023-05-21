import os, shutil, subprocess
os.chdir(os.path.dirname(__file__))
os.chdir("src")
subprocess.getoutput("python -m PyQt5.uic.pyuic -x main.ui -o modules" + os.sep + "exportedui.py")