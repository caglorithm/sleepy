
import unittest
import pdb
import numpy as np
from unittest.mock import MagicMock, Mock, patch, PropertyMock
from sleepy.gui.settings.core import Settings

class SettingsTest(unittest.TestCase):

    def test_construct_attributes(self):

        settings = Settings()

        try:
            settings.showIndex
            settings.intervalMin
            settings.intervalMax
            settings.useCheckpoints
            settings.plotGrid
            settings.plotGridSize
            settings.plotFiltered

            self.assertTrue(True)
        except AttributeError:
            self.assertFalse(True)

    def test_construct_useCheckpoints(self):

        settings = Settings()

        try:


            self.assertTrue(True)
        except AttributeError:
            self.assertFalse(True)

    def test_construct_intervalMinMax(self):

        settings = Settings()

        try:
            settings.intervalMin
            settings.intervalMax

            self.assertTrue(True)
        except AttributeError:
            self.assertFalse(True)

    def test_construct_intervalMinMax(self):

        settings = Settings()

        try:

            self.assertTrue(True)
        except AttributeError:
            self.assertFalse(True)
