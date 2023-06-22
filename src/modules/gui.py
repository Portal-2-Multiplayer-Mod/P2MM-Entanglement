from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from modules.exportedui import Ui_MainWindow
import sys, os
import threading, ctypes
import modules.launcher as launcher
import modules.functions as functions
from modules.logging import log
from modules.logging import GetNewLines
from time import sleep
import multiprocessing

def terminate(): # we need something to terminate the whole file in the case of a fault
    launcher.handlelockfile(True)
    sys.exit(0)

class NewlineThread(threading.Thread):
    curgloballine = 0

    def run(self):
        global ui
        if os.path.exists(launcher.bsdir + "portal2" + os.sep + "console.log"):
            os.remove(launcher.bsdir + "portal2" + os.sep + "console.log")

        scrollbar = ui.console_output.verticalScrollBar()
        while True:
            output = GetNewLines(self.curgloballine)
            self.curgloballine = output[1]
            newlines = output[0]

            # jankily append console newlines to newlines
            if launcher.gameisrunning:
                for line in launcher.getnewconsolelines(launcher.confilepath): newlines.append(line)


            is_at_bottom = False

            if len(newlines) > 0:
                is_at_bottom = scrollbar.value() >= scrollbar.maximum() - 60
                # if ui.console_output.toPlainText() == "":
                ui.console_output.append("\n".join(newlines))
                # else:
                #     ui.console_output.append("\n" + "\n".join(newlines))
                if is_at_bottom:
                    sleep(0.01)
                    scrollbar.setValue(scrollbar.maximum())

            # for line in newlines:
            #     ui.console_output.append(line)
            #     sleep(0.05)
            #     is_at_bottom = scrollbar.value() >= scrollbar.maximum() - 40
            #     if is_at_bottom:
            #         scrollbar.setValue(scrollbar.maximum())

            sleep(0.1) # we need to have a delay or else it fills up the loggers function calls

class LaunchThread(threading.Thread):
    def run(self):
        global heldproc
        # target function of the thread class
        heldproc = launcher.launchgame(rconpasswdlocal=functions.rconPassword)
        ui.start_button.setText("Stop")
        ui.start_button.setEnabled(True)

launcherthread = None

heldproc = None

def stop_game():
    global launcherthread
    global heldproc
    ui.start_button.setText("Stopping...")
    ui.start_button.setEnabled(False)
    # try:
    #     heldproc.terminate()
    # except:
    #     pass
    launcher.handlelockfile(True)
    ui.start_button.setText("Start")
    ui.start_button.clicked.disconnect(stop_game)
    ui.start_button.clicked.connect(launch_game)
    ui.start_button.setEnabled(True)

def launch_game():
    global launcherthread
    launcherthread = LaunchThread()
    launcherthread.daemon = True
    launcherthread.start()
    ui.console_output.setText("")
    launcher.curconsoleline = 0
    ui.start_button.setText("Game Is Starting...")
    ui.start_button.setEnabled(False)
    ui.start_button.clicked.disconnect(launch_game)
    ui.start_button.clicked.connect(stop_game)

commandlistpos = -1
def send_rcon():
    global commandlistpos
    if launcher.gameisrunning and launcher.RconReady:
        text = ui.command_line.text()
        output = functions.SendRcon(text, functions.rconPassword, hist=True)
        ui.command_line.setText("")
        commandlistpos = -1
        if len(output.strip()) > 0:
            log(output.strip(), "rcon")
    elif launcher.gameisrunning:
        log("user attempted to send command before rcon was ready")
    else:
        log("user attempted to send command while game is closed")

ui = None
def gui_main():
    global ui

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    newlinethread = NewlineThread()
    newlinethread.daemon = True
    newlinethread.start()

    ### UI LINKING

    def handle_key_press(event): # cycle previous commands when arrows are pressed
        global commandlistpos
        if event.key() == Qt.Key_Up:
            if len(functions.UserRconHist) == 0:
                commandlistpos = -1
                return

            commandlistpos += 1
            if commandlistpos > len(functions.UserRconHist) - 1:
                commandlistpos = len(functions.UserRconHist) - 1

            ui.command_line.setText(functions.UserRconHist[commandlistpos])
        elif event.key() == Qt.Key_Down:
            if len(functions.UserRconHist) == 0:
                commandlistpos = -1
                return

            commandlistpos -= 1
            if commandlistpos < 0:
                ui.command_line.setText("")
                commandlistpos = -1
                return

            ui.command_line.setText(functions.UserRconHist[commandlistpos])
        else:
            # allow the widget to process other key events normally
            QtWidgets.QLineEdit.keyPressEvent(ui.command_line, event)

    ui.send_button.clicked.connect(send_rcon)
    ui.command_line.returnPressed.connect(send_rcon)
    ui.command_line.keyPressEvent = handle_key_press

    ui.start_button.clicked.connect(launch_game)

    ###
    MainWindow.show()
    app.exec_()
    terminate()