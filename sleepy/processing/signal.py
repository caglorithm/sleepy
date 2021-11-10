
import numpy as np
from scipy.signal import find_peaks
from sleepy.processing.valley import Valley

class Signal:

    def __init__(self, data, samplingRate):

        self.data = data
        self.samplingRate = samplingRate

    @property
    def zeroCrossings(self):

        try:
            return self._zeroCrossings
        except AttributeError:

            signs = np.sign(self.data)

            # Treat 0 as a positive sign
            binarySigns = np.where(signs == 0, 1, signs)

            # https://stackoverflow.com/questions/3843017/efficiently-detect-sign-changes-in-python
            self._zeroCrossings = np.where(np.diff(binarySigns))[0]

            return self._zeroCrossings

    @property
    def posToNegZeroCrossings(self):

        try:
            return self._posToNegZeroCrossings
        except AttributeError:

            signs = np.sign(self.data)

            # Treat 0 as a positive sign
            binarySigns = np.where(signs == 0, 1, signs)

            # https://stackoverflow.com/questions/3843017/efficiently-detect-sign-changes-in-python
            self._posToNegZeroCrossings = np.where(np.diff(binarySigns) < 0)[0]

            return self._posToNegZeroCrossings

    @property
    def positivePeaks(self):

        try:
            return self._positivePeaks
        except AttributeError:

            self._positivePeaks, _ = find_peaks(self.data, height = 0)

            return self._positivePeaks

    def getNegativePeaks(self, negativeHeight):

        negativePeaks, _ = find_peaks(-self.data, height = negativeHeight)

        return negativePeaks

    def findValley(self, peak):

        try:

            nCrossing = self.findClosestNCrossing(peak)
            pCrossing = self.findClosestPCrossing(peak)

            nextPeak = list(filter(lambda p: p > pCrossing, self.positivePeaks))[0]

            return Valley(
                nCrossing,
                pCrossing,
                peak,
                nextPeak,
                self.data
            )

        except IndexError:
            pass

    def findClosestPCrossing(self, peak):

        cross = self.zeroCrossings

        pCrossing = list(filter(lambda c: c > peak, cross))[0]

        return pCrossing

    def findClosestNCrossing(self, peak):

        cross = self.zeroCrossings

        nCrossing = list(filter(lambda c: c < peak, cross))[-1]

        return nCrossing

    def findWaves(self):
        try:

            cross = self.posToNegZeroCrossings

            waves = []
            for i in range(len(cross) - 1):
                waves.append([cross[i],cross[i+1]])

            return waves

        except IndexError:
            pass
