
from sleepy.gui.tagging.model.event import Event
from scipy.signal import find_peaks
import numpy as np

class IntervalEvent(Event):
    def __init__(self, start, stop, dataSource, applicationSettings):

        super().__init__(dataSource, applicationSettings)

        self.interval = (start, stop)

    @property
    def label(self):
        return np.array(self._interval)

    @property
    def intervalCalc(self):

        return self._interval

    @intervalCalc.setter
    def intervalCalc(self, value):
        self._intervalCalc = value

    @property
    def interval(self):

        nInterval = self.convertSeconds(self.intervalMin)

        pInterval = self.convertSeconds(self.intervalMax)

        return (self._interval[0] - nInterval, self._interval[1] + pInterval)

    @interval.setter
    def interval(self, value):
        self._interval = value

    @property
    def intervalInSeconds(self):

        start = self.convertSamples(self._interval[0])
        end = self.convertSamples(self._interval[1])

        return (start, end)

    @property
    def point(self):

        return ( self._interval[0] + self._interval[1] ) / 2

    @property
    def currentPointInSeconds(self):

        timeStart = self.convertSamples(self._interval[0])
        timeEnd = self.convertSamples(self._interval[1])

        return ( timeStart + timeEnd ) / 2

    @property
    def minVoltage(self):

        relativeInterval = self.intervalCalc - self.epochInterval[0]

        return self.getVoltage(relativeInterval, method='min')

    @property
    def maxVoltage(self):

        relativeInterval = self.intervalCalc - self.epochInterval[0]

        return self.getVoltage(relativeInterval, method='max')

    def getVoltage(self, relativeInterval, method='min'):
        """Returns either the raw or filtered voltage amount for the point of
        this event.
        """

        if self.applicationSettings.plotFiltered:

            if method == 'min':

                return np.min(self.dataSource.epochFiltered[relativeInterval[0]:relativeInterval[1]])

            return np.max(self.dataSource.epochFiltered[relativeInterval[0]:relativeInterval[1]])

        else:
            if method == 'min':

                return np.min(self.dataSource.epoch[relativeInterval[0]:relativeInterval[1]])

            return np.max(self.dataSource.epoch[relativeInterval[0]:relativeInterval[1]])

    def plotSelected(self, axis):

        axis.axvspan(*self.intervalInSeconds, alpha = .5, color=self.applicationSettings.plotSelectedColor)

    def plotVisible(self, axis):

        axis.axvspan(*self.intervalInSeconds, alpha = .5, color="gray")

    def inInterval(self, interval):
        """Checks whether the event is inside of a given interval. This is true,
        if and only if the start of the event's interval is later than or equal to
        the start of the interval and is earlier or equal to the end of the interval.
        """

        return self._interval[0] >= interval[0] and self._interval[1] <= interval[1]
