from unittest.mock import MagicMock
import unittest
from sleepy.test.core import TestBase
from sleepy.gui.tagging.model.event import PointEvent
import numpy as np
import pdb

class EventTest(unittest.TestCase):

    def getSettings():

        settings = TestBase.getSettings()

        settings.intervalMin = 3.0
        settings.intervalMax = 3.0
        settings.plotFiltered = False

        return settings

    def getPointEvent(point, interval = (0,100)):
        """Creates a new point event for mocking.
        """

        settings = EventTest.getSettings()

        dataSource = TestBase.getDataSource(interval = interval)

        event = PointEvent(point, dataSource, settings)

        return event, dataSource, settings

    def newSettings():

        settings = MagicMock()
        settings.intervalMin = 3.0
        settings.intervalMax = 3.0
        settings.plotFiltered = False

        return settings

    def test_switchTag_single(self):
        """Switching the tag once should set the tag.
        """

        point, interval = 2, (0,7)

        event, _, _ = EventTest.getPointEvent(point, interval)

        event.switchTag()

        self.assertEqual(
            event.binaryTag,
            1
        )

    def test_switchTag_double(self):
        """Switching the tag double should reset the tag.
        """

        point, interval = 2, (0,7)

        event, _, _ = EventTest.getPointEvent(point, interval)

        event.switchTag()
        event.switchTag()

        self.assertEqual(
            event.binaryTag,
            0
        )
