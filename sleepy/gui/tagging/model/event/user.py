
from sleepy.gui.tagging.model.event.point import PointEvent
from functools import partial
import pdb

class UserPointEvent(PointEvent):

    def __init__(self, point, dataSource, applicationSettings):

        super().__init__(point, dataSource, applicationSettings)

        self.artist = None

        self.binaryTag = 0

    def plotSelected(self, axis):

        self.artist = axis.plot(
            *self.pointCoordinatesSeconds,
            marker='o',
            picker=5,
            c=self.applicationSettings.plotSelectedColor,
            markersize=self.applicationSettings.pointSize
        )[0]

    def plotVisible(self, axis):

        self.artist = axis.plot(
            *self.pointCoordinatesSeconds,
            marker='o',
            picker=5,
            c=self.applicationSettings.plotUserEventColor,
            markersize=self.applicationSettings.pointSize
        )[0]

    def switchTag(self):
        """Override super method. User events' tag cannot be switched.
        """

        pass
