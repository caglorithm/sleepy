from unittest.mock import MagicMock
import unittest
from sleepy.test.core import TestBase
from sleepy.gui.tagging.model.event import PointEvent
import numpy as np
import pdb

class PointTest(unittest.TestCase):

    def getSettings():

        settings = TestBase.getSettings()

        settings.intervalMin = 3.0
        settings.intervalMax = 3.0
        settings.plotFiltered = False

        return settings

    def getPointEvent(point, interval = (0,100)):
        """Creates a new point event for mocking.
        """

        settings = PointTest.getSettings()

        dataSource = TestBase.getDataSource(interval = interval)

        event = PointEvent(point, dataSource, settings)

        return event, dataSource, settings

    def test_point_plot_intervals_min_max_wider(self):
        """Test whether the correct data is plotted if the intervalMin, intervalMax
        settings are set to be wider than the actual epoch interval.
        This should display the whole epoch data.
        """

        point, interval = 2, (0,7)

        event, dataSource, settings = PointTest.getPointEvent(point, interval)

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

    def test_point_plot_intervals_min_max_narrower(self):
        """Test whether the correct data is plotted if the intervalMin, intervalMax
        settings are set to be narrower than the actual epoch interval.
        This should display only a part of the data.
        """

        point, interval = 2, (0,7)

        event, dataSource, settings = PointTest.getPointEvent(point, interval)

        # ensure 1,2,3 samples
        settings.intervalMin = 1 / dataSource.samplingRate
        settings.intervalMax = 1 / dataSource.samplingRate

        axis = MagicMock()
        axis.plot = MagicMock(return_value = [None])

        event.plot(axis)

        argumentsPlot = axis.plot.call_args_list[0][0]

        self.assertEqual(
            argumentsPlot[0].tolist(),
            (np.array([1,2,3]) / dataSource.samplingRate).tolist()
        )

        self.assertEqual(
            argumentsPlot[1].tolist(),
            np.array([dataSource.epoch[1],dataSource.epoch[2],dataSource.epoch[3]]).tolist()
        )

    def test_point_plot_other_events_in_range(self):
        """Point: Tests that events in the the same dataSource are plotted too,
        if they are in the visible range.
        """

        point, interval = 2, (0,7)

        event, dataSource, settings = PointTest.getPointEvent(point, interval)

        eventIn = PointEvent(3, dataSource, settings)
        eventIn.plotVisible = MagicMock()
        eventOut = PointEvent(6, dataSource, settings)
        eventOut.plotVisible = MagicMock()

        # ensure 1,2,3 samples
        settings.intervalMin = 1 / dataSource.samplingRate
        settings.intervalMax = 1 / dataSource.samplingRate

        axis = MagicMock()
        axis.plot = MagicMock(return_value = [None])

        event.plot(axis)

        eventIn.plotVisible.assert_called()
        eventOut.plotVisible.assert_not_called()
