
from sleepy.test.core import TestBase
from sleepy.gui.processing.core import Preprocessing
from sleepy.gui.processing.supported import SUPPORTED_DATASETS
from sleepy.processing.dataset import Dataset

import unittest
from unittest.mock import MagicMock, patch
import numpy as np

class MockingDataset(Dataset):

    @property
    def userLabels(self):
        """User labels are squeezed on channel level.
        """
        return [np.array([3,4]),np.array([3,5])]

    def getDataSource(self, channel, label):
        return TestBase.getDataSource()

class MockingOneUserLabelDataset(Dataset):

    @property
    def userLabels(self):
        """User labels are squeezed on channel level. Only one label in the first
        channel.
        """
        return [np.array([3]), np.array([])]

    def getDataSource(self, channel, label):
        return TestBase.getDataSource()

class MockingProcessor:
    """Mock object for a processor (algorithm or filter). Supplied with an id,
    this can be used to ensure that on algorithm or filter change the options
    are selected appropriatly.
    """

    def __init__(self, id):
        self.id = id

    @property
    def options(self):
        return self.id

class MockRendered:

    def __init__(self):
        self.rendered = False

    def render(self):
        self.rendered = True
        return self

class ProcessingTest(unittest.TestCase):

    def standardScenario(extension = "test"):
        """Creates a standard scenario for testing. Overrides SUPPORTED_DATASETS,
        to mock a dataset type.
        """

        _ , app, settings = TestBase.getBasics(active = False, name = "Test")

        app.supportedDatasets = { "TEST" : Dataset, "MOCK" : MockingDataset, "MOCK_SINGLE" : MockingOneUserLabelDataset }
        app.supportedFilters = app.supportedAlgorithms = []

        proc = ProcessingTest.getPreprocessing(app, extension)

        SUPPORTED_DATASETS = { "test" : Dataset }

        dataSource = TestBase.getDataSource()

        events = TestBase.getChannelEvents([
            [1,6,8],
            [2,5,6]
        ], settings, dataSource)

        return app, settings, proc, events

    def getPreprocessing(app, extension):

        proc = Preprocessing(app)

        proc.path = "path/to/test/file." + extension

        proc.view = MagicMock()

        return proc

    @patch('sleepy.gui.processing.core.Engine')
    def call(self, function, events_value, engine):
        """Patched call of a function calling engine.run in its core. Returns the
        engine_value to the caller.
        """

        engine.run = MagicMock(return_value = events_value)

        return function()

    def test_load_accepted(self):
        """Calling load leads to an accepted view (mocked).
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        self.call(proc.load, events)

        proc.view.accept.assert_called()

    def test_load_simple(self):
        """Calling load calls the Engine.run method with the only dataset
        available (test) and converts the returned events into a set of
        navigators.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        self.call(proc.load, events)

        self.assertEqual(proc.navigators[0].events, events[0])
        self.assertEqual(proc.navigators[1].events, events[1])

        self.assertTrue(isinstance(proc.dataset, Dataset))

    def test_load_userEvents_created(self):
        """Calling load leads to user events being created on the navigator.
        """

        app, settings, proc, events = ProcessingTest.standardScenario("mock")

        self.call(proc.load, events)

        self.assertEqual(
            [ e.point for e in proc.navigators[0].userEvents ],
            [3,4]
        )

        self.assertEqual(
            [ e.point for e in proc.navigators[1].userEvents ],
            [3,5]
        )

    def test_load_userEvents_created_single_user_label(self):
        """Calling load leads a single user event being created on the navigator.
        """

        app, settings, proc, events = ProcessingTest.standardScenario("mock_single")

        self.call(proc.load, events)

        self.assertEqual(
            [ e.point for e in proc.navigators[0].userEvents ],
            [3]
        )

        self.assertEqual(
            [ e.point for e in proc.navigators[1].userEvents ],
            []
        )

    def test_compute_view_output(self):
        """Calling compute leads to the view being called with the correct number
        of channels and number of events.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        self.call(proc.compute, events)

        proc.view.showNumberOfEvents.assert_called_with(6,2)

    def test_compute_file_not_supported(self):
        """Calling compute with a non supported file extension results in the
        view being called to display an error popup with the correct parameter.
        Further, the view is neither accepted nor rejected and the view also does
        display the number of events and channels.
        """

        app, settings, proc, events = ProcessingTest.standardScenario("notSupp")

        proc.view.showNumberOfEvents = MagicMock()
        proc.view.accept = MagicMock()
        proc.view.reject = MagicMock()

        self.call(proc.compute, events)

        proc.view.showNumberOfEvents.assert_not_called()
        proc.view.accept.assert_not_called()
        proc.view.reject.assert_not_called()

        proc.view.showFileNotSupported.assert_called_with("NOTSUPP")

    def test_load_file_not_supported(self):
        """Calling load with a non supported file extension results in the
        view being called to display an error popup with the correct parameter.
        Further, the view is neither accepted nor rejected and the navigators
        and the dataset do not change and are not used (enforced by assigning a
        string type beforehand).
        """

        app, settings, proc, events = ProcessingTest.standardScenario("notSupp")

        proc.view.accept = MagicMock()
        proc.view.reject = MagicMock()
        proc.dataset = "DatasetString"
        proc.navigators = "NavigatorsString"

        self.call(proc.load, events)

        proc.view.accept.assert_not_called()
        proc.view.reject.assert_not_called()

        proc.view.showFileNotSupported.assert_called_with("NOTSUPP")

        self.assertEqual(proc.dataset, "DatasetString")
        self.assertEqual(proc.navigators, "NavigatorsString")

    def test_onAlgorithmChange_no_algorithms(self):
        """Calling onAlgorithmChange without algorithms supported does not crash
        and causes the view to be called with no parameters.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        proc.onAlgorithmChange(0)

        proc.view.setNoAlgorithmParameters.assert_called()

    def test_onFilterChange_no_algorithms(self):
        """Calling onFilterChange without algorithms supported does not crash
        and causes the view to be called with no parameters.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        proc.onFilterChange(0)

        proc.view.setNoFilterParameters.assert_called()

    def test_construction_rendered(self):
        """Creating a Preprocessing instance causes the processors to be rendered.
        """

        _ , app, _ = TestBase.getBasics(active = False, name = "Test")

        app.supportedFilters = [MockRendered] * 30
        app.supportedAlgorithms = [MockRendered] * 30

        proc = ProcessingTest.getPreprocessing(app, "")

        [ self.assertTrue(a.rendered) for a in proc.algorithms[1:]]
        [ self.assertTrue(f.rendered) for f in proc.filters[1:]]

        self.assertEqual(proc.algorithms[0], None)
        self.assertEqual(proc.filters[0], None)


    def test_onAlgorithmChange_with_algorithms(self):
        """Calling onAlgorithmChange with algorithms supported causes the view
        to be called with the correct id from the MockingProcessor.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        proc.algorithms = [None, MockingProcessor("A"), MockingProcessor("B")]

        proc.onAlgorithmChange(1)

        proc.view.setAlgorithmParameters.assert_called_with("A")

        proc.onAlgorithmChange(2)

        proc.view.setAlgorithmParameters.assert_called_with("B")

        proc.onAlgorithmChange(1)

        proc.view.setAlgorithmParameters.assert_called_with("A")

    def test_onFilterChange_with_algorithms(self):
        """Calling onFilterChange with algorithms supported causes the view
        to be called with the correct id from the MockingProcessor.
        """

        app, settings, proc, events = ProcessingTest.standardScenario()

        proc.filters = [None, MockingProcessor("A"), MockingProcessor("B")]

        proc.onFilterChange(1)

        proc.view.setFilterParameters.assert_called_with("A")

        proc.onFilterChange(2)

        proc.view.setFilterParameters.assert_called_with("B")

        proc.onFilterChange(1)

        proc.view.setFilterParameters.assert_called_with("A")
