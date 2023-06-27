import sys
if sys.version_info[1] > 8:
    raise Exception('Requires Python 3.8 or lower')

from sleepy.gui.core import Gui

gui = Gui()
gui.run()
