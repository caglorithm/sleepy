
from unittest.mock import MagicMock
from sleepy.gui.tagging.model import Navigator
from sleepy.gui.tagging.model.event import PointEvent
from sleepy.gui.tagging.model import DataSource
from sleepy.processing.dataset import Dataset
import numpy as np

class TestBase:
    """Provides a set of constructors for different sleepy objects, potentially
    as MagicMock's. These constructors can be nested such that the usage in
    unit- and integration-tests is very flexible, i.e. objects to test can
    simply not be created via the :class:`TestBase`.
    """

    def getBasics(active, name):

        settings = TestBase.getSettings()

        app = TestBase.getApp(settings, name)

        view = TestBase.getView()

        return view, app, settings

    def getApp(settings, name = 'TestApplication'):

        app = MagicMock()
        app.name = name
        app.settings = settings

        appView = MagicMock()
        appView.control = app

        appView.window = MagicMock()

        return appView

    def getSettings():

        settings = MagicMock()
        settings.setWindowTitle = MagicMock()
        settings.showIndex = False
        settings.useCheckpoints = False
        return settings

    def getView():

        view = MagicMock()
        view.setButtonStyle = MagicMock()
        return view

    def getNavigator(events, changesMade = False):

        return Navigator(events, changesMade)

    def getDataset(path = ""):

        dataset = Dataset(None, path)
        dataset.save = MagicMock()

        # Is usually a property but cannot be mocked properly. As long as it
        # exists as an attribute, everything's fine.
        dataset.checkpoint = None
        return dataset

    def getPreprocessing(dataset = None, navigators = None):

        processing = MagicMock()
        processing.run = MagicMock(return_value=(navigators, dataset))
        return processing

    def getDataSource(filter = 1, samplingRate = 10, interval = (0,100)):

        return DataSource(
            np.arange(*interval, 1),
            np.arange(*interval, 1) / filter,
            interval,
            samplingRate = samplingRate
        )

    def getChannelEvents(points, settings, dataSource = None):

        return [
            TestBase.getEvents(pointList, settings, dataSource)
                for pointList in points
        ]

    def getEvents(points, settings, dataSource = None):

        return [ PointEvent(point, dataSource, settings) for point in points ]
