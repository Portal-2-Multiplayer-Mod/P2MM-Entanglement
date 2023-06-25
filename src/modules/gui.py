import sys, os, threading, subprocess
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from time import sleep
from qt_material import apply_stylesheet

from modules.exportedui import Ui_MainWindow
import modules.launcher as launcher
import modules.functions as fn
from modules.logging import GetNewLines
from modules.logging import log


# we need something to terminate the whole file in the case of a fault
def terminate():
    launcher.HandleLockFile(True)
    sys.exit(0)


class NewlineThread(threading.Thread):
    CurGlobalLine: int = 0

    def run(self):
        global Ui
        if os.path.exists(
            launcher.BuiltServerPath + "portal2" + os.sep + "console.log"
        ):
            os.remove(launcher.BuiltServerPath + "portal2" + os.sep + "console.log")

        scrollbar = Ui.console_output.verticalScrollBar()
        while True:
            output = GetNewLines(self.CurGlobalLine)
            self.CurGlobalLine = output[1]
            newlines = output[0]

            # jankily append console newlines to newlines
            if launcher.IsGameRunning:
                for line in launcher.GetNewConsoleLines(launcher.P2ConsoleLogPath):
                    newlines.append(line)

            is_at_bottom = False

            if len(newlines) > 0:
                is_at_bottom = scrollbar.value() >= scrollbar.maximum() - 60
                # if ui.console_output.toPlainText() == "":
                Ui.console_output.append("\n".join(newlines))
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

            sleep(
                0.1
            )  # we need to have a delay or else it fills up the loggers function calls


class GameThread(threading.Thread):
    """Holds the game's process"""

    GameProcess: subprocess.Popen[bytes] | None

    def run(self):
        # target function of the thread class
        self.GameProcess = launcher.LaunchGame(rconLocalPassword=fn.rconPassword)
        Ui.start_button.setEnabled(True)
        self.OnAfterThreadRun()

    def OnAfterThreadRun(self):
        if gameThread.GameProcess is not None:
            Ui.start_button.clicked.disconnect(StartGame)
            Ui.start_button.clicked.connect(TerminateGame)
            Ui.start_button.setText("Stop")
        else:
            Ui.start_button.setText("Start")


gameThread: GameThread
CommandListPos: int
Ui: Ui_MainWindow


def __init():
    global gameThread, CommandListPos, Ui

    gameThread = None
    CommandListPos = -1


def TerminateGame():
    global gameThread
    Ui.start_button.setText("Stopping...")
    Ui.start_button.setEnabled(False)
    # try:
    #     heldproc.terminate()
    # except:
    #     pass
    launcher.HandleLockFile(True)
    Ui.start_button.setText("Start")
    Ui.start_button.clicked.disconnect(TerminateGame)
    Ui.start_button.clicked.connect(StartGame)
    Ui.start_button.setEnabled(True)


def StartGame():
    global gameThread
    gameThread = GameThread()
    gameThread.daemon = True
    gameThread.start()
    Ui.console_output.setText("")
    launcher.CurConsoleLine = 0
    Ui.start_button.setText("Game Is Starting...")
    Ui.start_button.setEnabled(False)



def SendRcon():
    global CommandListPos
    if launcher.IsGameRunning and launcher.IsRconReady:
        text = Ui.command_line.text()
        output = fn.SendRcon(text, fn.rconPassword, hist=True)
        Ui.command_line.setText("")
        CommandListPos = -1
        if len(output.strip()) > 0:
            log(output.strip(), "rcon")
    elif launcher.IsGameRunning:
        log("user attempted to send command before rcon was ready")
    else:
        log("user attempted to send command while game is closed")


def Main():
    global Ui

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    apply_stylesheet(app, theme='p2mm.xml')
    MainWindow = QtWidgets.QWidget()
    Ui = Ui_MainWindow()
    Ui.setupUi(MainWindow)

    newlineThread = NewlineThread()
    newlineThread.daemon = True
    newlineThread.start()

    ### UI LINKING

    def handle_key_press(event):  # cycle previous commands when arrows are pressed
        global CommandListPos
        if event.key() == Qt.Key_Up:
            if len(fn.UserRconHist) == 0:
                CommandListPos = -1
                return

            CommandListPos += 1
            if CommandListPos > len(fn.UserRconHist) - 1:
                CommandListPos = len(fn.UserRconHist) - 1

            Ui.command_line.setText(fn.UserRconHist[CommandListPos])
        elif event.key() == Qt.Key_Down:
            if len(fn.UserRconHist) == 0:
                CommandListPos = -1
                return

            CommandListPos -= 1
            if CommandListPos < 0:
                Ui.command_line.setText("")
                CommandListPos = -1
                return

            Ui.command_line.setText(fn.UserRconHist[CommandListPos])
        else:
            # allow the widget to process other key events normally
            QtWidgets.QLineEdit.keyPressEvent(Ui.command_line, event)

    Ui.send_button.clicked.connect(SendRcon)
    Ui.command_line.returnPressed.connect(SendRcon)
    Ui.command_line.keyPressEvent = handle_key_press

    Ui.start_button.clicked.connect(StartGame)

    ###
    MainWindow.show()
    app.exec_()
    terminate()


__init()
