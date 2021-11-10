from unittest.mock import MagicMock
import unittest
from sleepy.test.core import TestBase
from sleepy.gui.tagging.model.event import IntervalEvent
import numpy as np
import pdb

class IntervalTest(unittest.TestCase):

    def getSettings():

        settings = TestBase.getSettings()

        settings.intervalMin = 3.0
        settings.intervalMax = 3.0
        settings.plotFiltered = False

        return settings

    def getIntervalEvent(label, interval = (0,100)):
        """Creates a new interval event for mocking.
        """

        settings = IntervalTest.getSettings()

        dataSource = TestBase.getDataSource(interval = interval)

        event = IntervalEvent(*label, dataSource, settings)

        return event, dataSource, settings

    def test_interval_plot_intervals_min_max_wider(self):
        """Test whether the correct data is plotted if the intervalMin, intervalMax
        settings are set to be wider than the actual epoch interval.
        This should display the whole epoch data.
        """

        label, interval = (3,5), (0,7)

        event, dataSource, settings = IntervalTest.getIntervalEvent(label, interval)

        # ensure wider than epochInterval
        settings.intervalMin = interval[1] / dataSource.samplingRate
        settings.intervalMax = interval[1] / dataSource.samplingRate

        axis = MagicMock()
        axis.plot = MagicMock(return_value = [None])

        event.plot(axis)

        argumentsPlot = axis.plot.call_args_list[0][0]

        self.assertEqual(
            argumentsPlot[0].tolist(),
            (np.array([0,1,2,3,4,5,6,7]) / dataSource.samplingRate).tolist()
        )

        self.assertEqual(
            argumentsPlot[1].tolist(),
            dataSource.epoch.tolist()
        )

    def test_interval_plot_intervals_min_max_narrower(self):
        """Test whether the correct data is plotted if the intervalMin, intervalMax
        settings are set to be narrower than the actual epoch interval.
        This should display only a part of the data.
        """

        label, interval = (3,5), (0,7)

        event, dataSource, settings = IntervalTest.getIntervalEvent(label, interval)

        # ensure 2,3,4,5,6 samples
        settings.intervalMin = 1 / dataSource.samplingRate
        settings.intervalMax = 1 / dataSource.samplingRate

        axis = MagicMock()
        axis.plot = MagicMock(return_value = [None])

        event.plot(axis)

        argumentsPlot = axis.plot.call_args_list[0][0]

        self.assertEqual(
            argumentsPlot[0].tolist(),
            (np.array([2,3,4,5,6]) / dataSource.samplingRate).tolist()
        )

        self.assertEqual(
            argumentsPlot[1].tolist(),
            np.array([dataSource.epoch[2],dataSource.epoch[3],dataSource.epoch[4],dataSource.epoch[5],dataSource.epoch[6]]).tolist()
        )

    def test_interval_plot_other_events_in_range(self):
        """Interval: Tests that events in the the same dataSource are plotted too,
        if they are in the visible range.
        """

        label, interval = (2,3), (0,7)

        event, dataSource, settings = IntervalTest.getIntervalEvent(label, interval)

        eventIn = IntervalEvent(3,4, dataSource, settings)
        eventIn.plotVisible = MagicMock()
        eventOut = IntervalEvent(6,7, dataSource, settings)
        eventOut.plotVisible = MagicMock()

        # Start is inside of visible area, but end is not
        eventOutOverlap = IntervalEvent(3,5, dataSource, settings)
        eventOutOverlap.plotVisible = MagicMock()

        # ensure 2,3,4 samples
        settings.intervalMin = 1 / dataSource.samplingRate
        settings.intervalMax = 1 / dataSource.samplingRate

        axis = MagicMock()
        axis.plot = MagicMock(return_value = [None])

        event.plot(axis)

        eventIn.plotVisible.assert_called()
        eventOut.plotVisible.assert_not_called()
        eventOutOverlap.plotVisible.assert_not_called()
