
from PyQt5.QtWidgets import QApplication
from sleepy.gui.view import View
from sleepy.gui.settings.core import Settings
from sleepy.gui.exceptions import UserCancel
from sleepy.gui.processing.supported import SUPPORTED_FILTERS, SUPPORTED_ALGORITHMS, SUPPORTED_DATASETS

class Gui(QApplication):
    """Used to load the GUI. It builds the starting window and sets a provisional
    GUI title as well as an icon. Inherits form :class:`PyQt5.QApplication`.
    """

    def __init__(self):
        """Configures the application, creates application settings and creates
        the view that wraps around every GUI element.
        """

        super().__init__(list())

        self.name = "Sleepy"

        self.setOrganizationName("pupuis@github")
        self.setApplicationName(self.name)

        self.__setSupported()

        #QSettings().clear()

        self.settings = Settings(self, self.onRefresh)

        self.view = View(self)

        self.view.setNull()

        self.tagging = False

    def run(self):
        """Start the application.
        """

        self.view.open()

        self.exec_()

    def onOpenFile(self):
        """Triggered when the user wants to open a new file to work with.
        """

        try:
            self.view.setTagging()
        except UserCancel:
            pass

    def onRefresh(self):
        """Refreshes the tagging view which e.g. applies all latest changes to
        the changes.
        """

        self.view.refreshTagging()

    def onClearFile(self):
        """Triggered when the user wants to clear the currently loaded file.
        """

        try:
            self.view.setNull()
        except UserCancel:
            pass

    def onReloadFile(self):
        """Reload the latest fileLoader. This should only work if a file has
        recently been opened.
        """

        pass

    def closeEvent(self, event):
        """Triggered when the user wants to close the application.
        """

        try:

            self.view.setNull()

            event.accept()

        except UserCancel:

            event.ignore()

    def __setSupported(self):
        """Sets the constant supported objects as an attribute of this class.
        """

        self.supportedDatasets   = SUPPORTED_DATASETS
        self.supportedFilters    = SUPPORTED_FILTERS
        self.supportedAlgorithms = SUPPORTED_ALGORITHMS
