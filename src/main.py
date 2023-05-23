import os, time, multiprocessing
import modules.gui as gui
import modules.functions as functions
import modules.launcher as launcher
import modules.logging as logging

os.chdir(os.path.abspath(os.path.dirname(__file__)))

### gui

gui.gui_main()
###