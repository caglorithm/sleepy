from PyQt5.QtWidgets import QMainWindow, QAction, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QStackedWidget
from PyQt5.QtGui import QIcon
from sleepy.gui.tagging.view import NullView, TaggingView
from sleepy.gui.tagging.control import TaggingControl
from sleepy.gui.processing.core import Preprocessing
import os

def closingTagging(function):
    """Decorator for methods that can only be executed if the tagging control
    can be closed properly. Must have an instance of :class:`TaggingControl` as
    its attribute with the name 'taggingControl'. This decorator is mostly aimed
    at the sleepy.gui.view.View.
    """

    def close(self, *args):

        self.taggingControl.close()

        function(self, *args)

    return close

class View:
    """View of the main application. Creates the GUI and abstracts some common
    behaviour around the screen elements.
    """

    def __init__(self, control):
        """Sets a given control and creates the screen elements.

        :param control: The control to this view (implementing application logic).
        """

        self.control = control

        self.__initializeWindow(control.name)

    def open(self):
        """Show the application window.
        """

        self.window.show()

    @closingTagging
    def setNull(self):
        """Abstraction around setting the null view as the current widget.
        """

        self.nullView.open()

        self.views.setCurrentWidget(self.nullView)

    @closingTagging
    def setTagging(self):
        """Abstraction around setting the tagging view as the current widget.
        """

        preprocessing = Preprocessing(self.control)

        self.taggingControl.open(preprocessing)

        self.views.setCurrentWidget(self.taggingView)

    def refreshTagging(self):
        """Abstraction around refreshing the tagging control.
        """

        self.taggingControl.refresh()

    def closeTagging(self):
        """Abstraction around closing the tagging control.

        :raises UserCancel: Raised if the user aborts the closing process.
        """

        self.taggingControl.close()

    def __initializeWindow(self, name):
        """Create the main window.
        """

        self.window = QMainWindow()

        self.window.setWindowTitle(name)

        self.window.setMinimumWidth(800)
        self.window.setMinimumHeight(600)

        self.window.closeEvent = self.control.closeEvent

        self.__initializeIcon()
        self.__initializeMenu()
        self.__initializeShortcuts()
        self.__initializeCentralWidget()

    def __initializeIcon(self):
        """Sets an icon to the window.
        """

        path = os.path.dirname(os.path.realpath(__file__))

        iconObject = QIcon(path + os.path.sep + "icons/ToyIcon.bmp")

        self.window.setWindowIcon(iconObject)

    def __initializeCentralWidget(self):
        """Create the central widget of the window, which is a stacked widget
        with which one can switch between different views. Creates two views:
        One for the null screen and one for the tagging screen.
        """

        self.views = QStackedWidget()

        self.taggingControl = TaggingControl(self, self.control.settings)
        self.taggingView = TaggingView(self, self.taggingControl, self.control.settings)
        self.taggingControl.view = self.taggingView

        self.nullView = NullView(self)

        self.views.addWidget(self.taggingView)
        self.views.addWidget(self.nullView)

        self.window.setCentralWidget(self.views)

    def __initializeMenu(self):
        """Builds the menu bar and connects the handler-methods of the control
        to the respective events.
        """

        applicationMenuBar = self.window.menuBar()

        fileMenu = applicationMenuBar.addMenu('File')
        openFile = QAction('Open', self.window)
        openFile.triggered.connect(self.control.onOpenFile)
        fileMenu.addAction(openFile)

        self.saveFile = QAction('Save', self.window)
        fileMenu.addAction(self.saveFile)

        self.clearFile = QAction('Clear', self.window)
        self.clearFile.triggered.connect(self.control.onClearFile)
        fileMenu.addAction(self.clearFile)

        self.reloadFile = QAction('Reload', self.window)
        self.reloadFile.triggered.connect(self.control.onReloadFile)
        fileMenu.addAction(self.reloadFile)

        userMenu = applicationMenuBar.addMenu('User')
        settings = QAction('Settings', self.window)
        settings.triggered.connect(self.control.settings.asDialog)
        userMenu.addAction(settings)

    def __initializeShortcuts(self):
        """Registers keyboard shortcuts for the most common functionality.
        """

        openFile = QShortcut(QKeySequence("Ctrl+O"), self.window)
        openFile.activated.connect(self.control.onOpenFile)

        openSettings = QShortcut(QKeySequence("Ctrl+Q"), self.window)
        openSettings.activated.connect(self.control.settings.asDialog)

        openSettings = QShortcut(QKeySequence("Ctrl+R"), self.window)
        openSettings.activated.connect(self.control.onReloadFile)

        #openSettings2 = QShortcut(QKeySequence("Ctrl+S"), self.window)
        #openSettings2.activated.connect(self.taggingControl.onSaveFile)
