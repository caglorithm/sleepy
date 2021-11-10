
from PyQt5.QtCore import pyqtRemoveInputHook, pyqtRestoreInputHook

class SleepyDebug:
    """Due to issues with debugging with pdb in PyQt5 (https://stackoverflow.com/questions/1736015/debugging-a-pyqt4-app),
    this class provides a tool to debug the sleepy application. The idea is to
    open the application for debugging, do the debugging and then close it again.
    This is realized via a simple decorator. The pdb.set_trace must still be called.
    The decorator import pdb by default.
    """
    pass

def tracing(function):

    def debug(*args):

        pyqtRemoveInputHook()

        result = function(*args)

        pyqtRestoreInputHook()

        return result

    return debug
