import sys
from PySide6 import QtCore, QtWidgets, QtGui
import multiprocessing
import launcher
import numpy as np
import threading
import sys
import os
import time

os.chdir(os.path.abspath(os.path.dirname(__file__)))

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("P2MM Launcher")

        self.output_rd = QtWidgets.QTextBrowser()
        self.output_rd.setObjectName("output_rd")

        self.launchbutton = QtWidgets.QPushButton("launch game!")

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.output_rd)
        self.layout.addWidget(self.launchbutton)

        self.launchbutton.clicked.connect(self.launchbuttonfunc)

    launchproc = None
    gamerunning = False

    @QtCore.Slot()
    def launchbuttonfunc(self):
        if not self.gamerunning:
            print("game launch pressed calling launchgame")
            args = "+echo p2mm +mp_dev_wait_for_other_player 0 +map mp_coop_lobby_3 +developer 1 -textmode -novid -nosound -nojoy -noipx -nopreload -norebuildaudio -condebug -refresh 30 -allowspectators -threads " + str(multiprocessing.cpu_count())
            self.launchproc = multiprocessing.Process(target=launcher.launchgame, args=(launcher.bsdir, args))
            self.launchproc.start()
            self.gamerunning = True
            self.launchbutton.setText("stop game!")
            if os.path.isfile(launcher.bsdir + "portal2/console.log"):
                os.remove(launcher.bsdir + "portal2/console.log")
            consolethread.start()
        else:
            terminategame()
            self.gamerunning = False
            self.launchbutton.setText("launch game!")

def terminategame():
    try:
        widget.launchproc.terminate()
    except:
        pass
    launcher.handlelockfile(True)

class ConsoleOutputThread(threading.Thread):
    def __init__(self, sleep_interval=0.1):
        super().__init__()
        self._kill = threading.Event()
        self._interval = sleep_interval

    def run(self):
        while True:
            for line in launcher.getnewconsolelines(launcher.bsdir + "portal2" + os.sep + "console.log"):
                widget.output_rd.append(line.strip())
                time.sleep(0.02)
                widget.output_rd.moveCursor(QtGui.QTextCursor.MoveOperation.End)
                widget.output_rd.ensureCursorVisible()

            is_killed = self._kill.wait(self._interval)
            if is_killed:
                break

        print("killing console thread")

    def kill(self):
        self._kill.set()

consolethread = ConsoleOutputThread()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    # start the thread for grabbing console output

    # wait for app to exit and gracefully shutdown
    app.exec()
    consolethread.kill()
    terminategame()
    sys.exit()