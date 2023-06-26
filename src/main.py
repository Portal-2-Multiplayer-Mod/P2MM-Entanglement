import os, sys, signal
import modules.Configs as cfg
import modules.gui as gui
from modules.launcher import HandleLockFile
from modules.logging import log
import modules.functions as fn


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
    HandleLockFile()
    sys.exit(0)


if __name__ == "__main__":
    if fn.GetSystem() == "darwin":
        log("We do not support MacOS, nor do we plan to. However, you can still join other P2MM servers from a mac client.")
        exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    #todo: we really need to stop using 'chdir' it's really bad
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    cfg.LoadConfigs()
    gui.Main()
