
from sleepy.gui.processing.view import PreprocessingView
from sleepy.gui.exceptions import UserCancel
from sleepy.gui.tagging.model import Navigator
from sleepy.processing.engine import Engine
from sleepy.gui.tagging.model.event.user import UserPointEvent
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QSettings
import numpy as np

class Preprocessing:
    """Application starting a preprocessing screen from which the user can
    select a dataset, a filter and a algorithm. Uses the :class:`Engine` class
    to produce a list of navigators and returns them to the caller.
    """

    def __init__(self, parent):
        """Configures the application by setting a default path, creating the
        :class:`QDialog` and rendering filters and algorithms.

        :param parent: The parent application.

        :raises UserCancel: The user cancelled the initial path selection and thus,
        wants to abort the preprocessing.
        """

        self.path = ""
        self.parent = parent
        self.algorithms = self.__renderAlgorithms()
        self.filters = self.__renderFilters()
        self.algorithm = None
        self.filter = None

    def compute(self):
        """Compute events with the given settings but do not create navigators
        yet. The result of the computation is displayed to the user via the view.
        """

        try:
            events, _ = self.__computeEvents()
        except UserCancel:
            return

        numberOfEvents = sum([ len(eventList) for eventList in events ])
        numberOfChannels = len(events)

        self.view.showNumberOfEvents(numberOfEvents, numberOfChannels)

    def load(self):
        """Load navigators from events computed with the given settings. Calls
        the accept method of the view to accept the dialog and return to the
        calling method (Preprocessing.run).
        """

        try:
            events, dataset = self.__computeEvents()
        except UserCancel:
            return

        self.dataset = dataset

        channels = range(len(events))

        self.navigators = [
            self.__prepareNavigator(channel, events[channel], dataset)
                for channel in channels
        ]

        self.view.accept()

    def onAlgorithmChange(self, index):
        """Called on change of algorithm selection. Sets the algorithm with
        the corresponding index and tries to set the algorithm's parameters
        to the view.

        :param index: Index of the algorithm to select.
        """

        self.algorithm = self.algorithms[index]

        try:

            self.view.setAlgorithmParameters(self.algorithm.options)

        except AttributeError:

            self.view.setNoAlgorithmParameters()

    def onFilterChange(self, index):
        """Called on change of filter selection. Sets the filter with
        the corresponding index and tries to set the filter's parameters
        to the view.

        :param index: Index of the filter to select.
        """

        self.filter = self.filters[index]

        try:

            self.view.setFilterParameters(self.filter.options)

        except AttributeError:

            self.view.setNoFilterParameters()

    def selectPath(self):
        """Tries to load the path to a new dataset. Loads the property recentPath
        from disk to find a recent path selected. If the user confirms a path
        said path is saved on disk as the new recentPath.
        """

        recentPath = QSettings().value("recentPath")

        path, _ = QFileDialog.getOpenFileName(self.parent.view.window, 'Open File', recentPath)
        if path != '':

            self.view.setPath(path)

            self.path = path

            QSettings().setValue("recentPath", path)

    def run(self):
        """Runs the preprocessing by starting the view's window and returns the
        computed navigators in Preprocessing.load. If the navigators were not
        computed then the window must have been rejected. This is propagated
        forward by raising UserCancel.

        Hint for unit testing: This method should not be called under test.
        Every other public method can be tested in isolation, this method
        essentially creates a view and starts the window.

        :returns: A list of navigators, one for each channel and a dataset.

        :raises UserCancel: Window was rejected by the user.
        """

        self.view = PreprocessingView(self.parent.view.window, self)

        # Initially do not catch the UserCancel to signal the initial cancel
        # to the parent
        self.selectPath()

        if self.path == "":

            raise UserCancel

        self.view.exec_()

        try:
            return self.navigators, self.dataset
        except AttributeError:
            raise UserCancel

    def __prepareNavigator(self, channel, eventList, dataset):
        """Creates a new navigator instance and adds the user labels from the
        dataset.
        """

        navigator = Navigator(eventList, dataset.changesMade)

        if channel < len(dataset.userLabels):

            for userLabel in np.array([dataset.userLabels[channel].squeeze()]).ravel():

                dataSource = self.dataset.getDataSource(channel, userLabel)

                userEvent = UserPointEvent(userLabel, dataSource, self.parent.settings)

                navigator.addCreatedUserEvent(userEvent)

                navigator.onSave()

        return navigator

    def __computeEvents(self):
        """Computes the events given algorithm and filter. The dataset is also
        loaded at this step based on the path that is currently selected.
        The settings are inherited from the parent. Note that in this case 'parent'
        does not refer to a super-class but to the application calling this
        application.
        """

        dataset = self.__loadDataset()

        try:

            settings = self.parent.settings

            return Engine.run(self.algorithm, self.filter, dataset, settings), dataset

        except AttributeError:
            return dataset.labels, dataset

    def __loadDataset(self):
        """Loads a :class:`Dataset` instance based on the path currently selected.
        Parses the path to find the file extension and finds the appropriate
        instance via the supported file. The resulting class must implement a
        static load method that returns a raw data object with which an instance
        of said class can be constructed.
        """

        extension = self.__getFileExtension()

        DatasetClass = self.__findSupportedAttempt(extension)

        raw = DatasetClass.load(self.path)

        return DatasetClass(raw, self.path)

    def __findSupportedAttempt(self, extension):
        """Tries to find a suitable dataset for a given extension in the supported
        file. If that attempt fails, then a pop-up is shown to the user and a
        UserCancel is issued.
        """

        try:
            return self.parent.supportedDatasets[extension]
        except KeyError:

            self.view.showFileNotSupported(extension)

            raise UserCancel

    def __renderFilters(self):
        """Renders the list of supported filters, drawn from the supported
        file. At the top of the list is a NoneType, indicating that no
        filter was selected.
        """

        return [None] + [ f().render() for f in self.parent.supportedFilters ]

    def __renderAlgorithms(self):
        """Renders the list of supported algorithms, drawn from the supported
        file. At the top of the list is a NoneType, indicating that no
        algorithm was selected.
        """

        return [None] + [ a().render() for a in self.parent.supportedAlgorithms ]

    def __getFileExtension(self):
        """Returns the file extension of the current path in upper-case letters.
        """

        return self.path.rsplit('.', 1)[-1].upper()
