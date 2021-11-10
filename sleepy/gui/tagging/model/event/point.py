
from sleepy.gui.tagging.model.event import Event
import pdb

class PointEvent(Event):
    def __init__(self, point, dataSource, applicationSettings):

        super().__init__(dataSource, applicationSettings)

        self.point = point

    @property
    def label(self):
        return self.point

    @property
    def amplitude(self):

        relativePoint = self.point - self.epochInterval[0]

        return self.getVoltage(relativePoint)

    @property
    def interval(self):

        point = self.point

        nInterval = self.convertSeconds(self.intervalMin)

        pInterval = self.convertSeconds(self.intervalMax)

        return (point - nInterval, point + pInterval)

    @property
    def pointCoordinatesSeconds(self):

        time = self.convertSamples(self.point)

        relativePoint = self.point - self.epochInterval[0]

        voltage = self.getVoltage(relativePoint)

        return (time, voltage)

    @property
    def currentPointInSeconds(self):
        return self.pointCoordinatesSeconds[0]

    def getVoltage(self, relativePoint):
        """Returns either the raw or filtered voltage amount for the point of
        this event.
        """

        if self.applicationSettings.plotFiltered:

            return self.dataSource.epochFiltered[relativePoint]

        else:

            return self.dataSource.epoch[relativePoint]

    def plotSelected(self, axis):

        axis.plot(
            *self.pointCoordinatesSeconds,
            marker='o',
            c=self.applicationSettings.plotSelectedColor,
            markersize=self.applicationSettings.pointSize
        )

    def plotVisible(self, axis):

        if self.tagged:
            color = "red"
        else:
            color = "gray"

        axis.plot(
            *self.pointCoordinatesSeconds,
            marker='o',
            color=color,
            markersize=self.applicationSettings.pointSize
        )

    def inInterval(self, interval):

        return self.point >= interval[0] and self.point <= interval[1]
