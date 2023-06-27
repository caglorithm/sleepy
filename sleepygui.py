import sys
if sys.version_info[1] > 7:
    raise Exception('Requires Python 3.7 or lower')

from sleepy.gui.core import Gui

gui = Gui()
gui.run()
