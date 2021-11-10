
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLineEdit, QDialogButtonBox, QDialog, QMessageBox
from PyQt5.QtWidgets import QHBoxLayout, QGroupBox, QWidget, QComboBox, QStackedWidget, QLabel

class PreprocessingView(QDialog):

    def __init__(self, app, control):
        """The view corresponding to controller class :class:`Preprocessing`.
        Constructs the widgets and displays them in a dialog window.

        :param app: Instance of :class:`QMainWindow`.

        :param control: Instance of :class:`Preprocessing` which functions as
        the controller of this view.
        """

        super().__init__(app)

        self.control = control

        self.setWindowTitle("Preprocessing")
        self.setMinimumWidth(600)

        self.__initializeLayout()

    def __initializeLayout(self):
        """Constructs the outer layout of the dialog and calls all initializations
        of the elements of that layout: A path selector for the dataset, an options
        layout containing algorithm and filter selection and a button box controlling
        the interactions with the dialog.
        """

        self.layout = QVBoxLayout(self)

        self.__initializePathSelector()
        self.__initializeOptions()
        self.__initializeButtonBox()

    def __initializePathSelector(self):
        """Constructs a group box containing a path selector with which the user
        can choose the path to the dataset.
        """

        self.pathSelectorBox = QGroupBox('Dataset')

        self.pathSelectorLayout = QHBoxLayout()

        self.pathEdit = QLineEdit(self.control.path)
        self.pathSelectorLayout.addWidget(self.pathEdit)

        self.changePathButton = QPushButton('...')
        self.changePathButton.clicked.connect(self.control.selectPath)

        self.pathSelectorLayout.addWidget(self.changePathButton)

        self.pathSelectorBox.setLayout(self.pathSelectorLayout)

        self.layout.addWidget(self.pathSelectorBox)

    # https://doc.qt.io/archives/qq/qq19-buttons.html#
    def __initializeButtonBox(self):
        """Constructs the buttons at the bottom margin of the dialog. Supported
        actions are load, compute and cancel.
        """

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Load", QDialogButtonBox.AcceptRole)
        self.buttonBox.accepted.connect(self.control.load)

        self.computeButton = QPushButton("Compute")
        self.buttonBox.addButton(self.computeButton, QDialogButtonBox.ActionRole)
        self.computeButton.clicked.connect(self.control.compute)

        self.buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)

    def __initializeOptions(self):
        """Constructs two group boxes. One for the filter and one for the algorithm
        selection.
        """

        self.optionsWidget = QWidget()

        self.optionsLayout = QVBoxLayout()

        self.optionsLayout.addWidget(self.__getFilterOptions())

        self.optionsLayout.addWidget(self.__getAlgorithmOptions())

        self.optionsLayout.addWidget(self.computationStatus)

        self.optionsWidget.setLayout(self.optionsLayout)

        self.layout.addWidget(self.optionsWidget)

    @property
    def computationStatus(self):
        """Returns a label containing the written result of the latest computation.
        """

        try:
            return self._computationStatus
        except AttributeError:

            self._computationStatus = QLabel("")
            return self._computationStatus

    def __getFilterOptions(self):
        """Constructs the layout containing the filter selection.
        """

        self.filterSelection = QComboBox()

        self.filterSelection.addItem("No filter")

        list(map(
            lambda f: self.filterSelection.addItem(f.name),
            self.control.filters[1:]
        ))

        self.filterBox = QGroupBox('Filters')

        layout = QVBoxLayout()

        layout.addWidget(self.filterSelection)

        self.filterParameters = QStackedWidget()

        self.noFilterParameters = QWidget()
        self.filterParameters.addWidget(self.noFilterParameters)

        list(map(
            lambda f: self.filterParameters.addWidget(f.options),
            self.control.filters[1:]
        ))

        layout.addWidget(self.filterParameters)

        self.filterBox.setLayout(layout)

        self.filterSelection.currentIndexChanged.connect(self.control.onFilterChange)

        return self.filterBox

    def __getAlgorithmOptions(self):
        """Constructs the layout containing the algorithm selection.
        """

        self.algorithmSelection = QComboBox()

        self.algorithmSelection.addItem("No processing")

        list(map(
            lambda a: self.algorithmSelection.addItem(a.name),
            self.control.algorithms[1:]
        ))

        self.algorithmBox = QGroupBox('Algorithms')

        layout = QVBoxLayout()

        layout.addWidget(self.algorithmSelection)

        self.algorithmParameters = QStackedWidget()

        self.noParameters = QWidget()
        self.algorithmParameters.addWidget(self.noParameters)

        list(map(
            lambda a: self.algorithmParameters.addWidget(a.options),
            self.control.algorithms[1:]
        ))

        layout.addWidget(self.algorithmParameters)

        self.algorithmBox.setLayout(layout)

        self.algorithmSelection.currentIndexChanged.connect(self.control.onAlgorithmChange)

        return self.algorithmBox

    def setPath(self, path):
        """Abstraction around setting the text of the pathEdit widget.

        :param path: The updating path to the dataset.
        """

        self.pathEdit.setText(path)

    def setNoAlgorithmParameters(self):
        """Select that no algorithm parameters can be chosen.
        """

        self.algorithmParameters.setCurrentWidget(self.noParameters)

    def setNoFilterParameters(self):
        """Select that no filter parameters can be chosen.
        """

        self.filterParameters.setCurrentWidget(self.noFilterParameters)

    def setAlgorithmParameters(self, parameters):
        """Set the options view displaying the algorithm parameters.

        :param parameters: A :class:`QWidget` containing the parameters.
        """

        self.algorithmParameters.setCurrentWidget(parameters)

    def setFilterParameters(self, parameters):
        """Set the options view displaying the filter parameters.

        :param parameters: A :class:`QWidget` containing the parameters.
        """

        self.filterParameters.setCurrentWidget(parameters)

    def showNumberOfEvents(self, numberOfEvents, numberOfChannels):
        """Abstraction around setting the text to the computationStatus
        widget, formatting the number of events and the number of channels
        supplied.

        :param numberOfEvents: The number of events.

        :param numberOfChannels: The number of channels.
        """

        self.computationStatus.setText(
            "{} events found in {} channels.".format(
                numberOfEvents,
                numberOfChannels
            )
        )

        self.computationStatus.repaint()

    def showFileNotSupported(self, extension):
        """Show a pop-up window, notifying the user that the file type is not
        supported.

        :param extension: The unsupported exension as a string.
        """

        error = QMessageBox(self.window)
        error.setWindowTitle('Error')
        error.setIcon(QMessageBox.Critical)
        error.setText(
            'Files of type .{} are not supported.'.format(extension.lower())
        )
        error.exec_()
