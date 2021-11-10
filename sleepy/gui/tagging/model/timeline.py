
import numpy as np
import pdb
from matplotlib.ticker import FuncFormatter
import time

class Timeline:

    def __init__(self, axis, settings):

        self.axis = self.customizeAxis(axis)

        self.settings = settings

    def plot(self, points, currentPoint, currentInterval):
        """Plots a timeline on a given axis, which is specified by a set of
        gray lines marking the events, a coral line marking the currently
        selected event and a blue interval marking the currently selected time-
        window.
        """

        self.plotPoints(points)

        self.interval = self.plotCurrentInterval(currentInterval)

        self.point = self.plotCurrentPoint(currentPoint)

    def update(self, currentPoint, currentInterval):
        """Updates the position of the current point and the current interval
        but leaves the set of darkgrey vertical lines untouched.
        """

        self.updateCurrentInterval(currentInterval)

        self.updateCurrentPoint(currentPoint)

    def customizeAxis(self, axis):
        """Performs a sequence of customization steps for the axis to ensure
        its proper presentation. The axis object is modified and not copied.
        """

        axis.set_ylim(0,1)

        axis.yaxis.set_visible(False)

        axis.xaxis.set_ticks_position('bottom')

        axis.xaxis.set_major_formatter(
            FuncFormatter(lambda sec, x: time.strftime('%H:%M:%S', time.gmtime(sec)))
        )

        axis.get_yaxis().set_ticklabels([])

        return axis

    def plotPoints(self, points):
        """Plots given points as a set of darkgrey vertical lines on a given
        axis.
        """

        list(map(lambda x: self.axis.axvline(x, c = 'darkgrey'), points))

    def plotCurrentInterval(self, currentInterval):
        """Plots a given interval as a span in standard color.
        """

        return self.axis.axvspan(*currentInterval, alpha=.7)

    def plotCurrentPoint(self, currentPoint):
        """Plots a given point as a coral vertical line.
        """

        return self.axis.axvline(currentPoint, linewidth=2 ,c=self.settings.plotSelectedColor)

    def updateCurrentInterval(self, currentInterval):
        """Updates the plot of an interval as a span in standard color.
        """

        start, end = currentInterval

        xy = np.array([
            [start, 0],
            [start, 1],
            [end, 1],
            [end, 0],
            [start, 0]
        ])

        self.interval.set_xy(xy)

    def updateCurrentPoint(self, currentPoint):
        """Updates the plot of a given point as a coral vertical line.
        """

        self.point.set_xdata(currentPoint)
        self.point.set_color(self.settings.plotSelectedColor)
