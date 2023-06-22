import os, sys, signal
import modules.gui as gui
import modules.launcher as launcher
from modules.logging import log


def sigint_handler(signal, frame) -> None:
    """Deletes the lock file on launcher exit

    Parameters
    ----------
    signal : _type_
        _description_
    frame : _type_
        _description_
    """

    log("\n>EXIT SIGNAL RECEIVED TERMINATING<\n")
    launcher.HandleLockFile()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, sigint_handler)

    #todo: we really need to stop using 'chdir' it's really bad
    os.chdir(os.path.abspath(os.path.dirname(__file__)))

    gui.Main()
