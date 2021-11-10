from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
from scipy.signal import find_peaks
import numpy as np

class Custom(Algorithm):

    def __init__(self):

        self.name = "Custom Implementation"

        self.durationLow = Parameter(
            title = "Lower bound for duration interval [sec]",
            fieldType = float,
            default = 0.2
        )

        self.durationHigh = Parameter(
            title = "Upper bound for duration interval [sec]",
            fieldType = float,
            default = 7.0
        )

        self.firstCrosstoMinDuration = Parameter(
            title = "Max. duration from first zero crossing to negative wave peak [sec]",
            fieldType = float,
            default = 2.0
        )

        self.minToMaxDuration = Parameter(
            title = "Max. duration from negative to positive wave peak [sec]",
            fieldType = float,
            default = 2.0
        )

        self.maxToSecondZeroCrossDuration = Parameter(
            title = "Max. duration from positive wave peak to second zero crossing [sec]",
            fieldType = float,
            default = 4.0
        )

        self.nPosPeaks = Parameter(
            title = "Max. number of positive peaks",
            fieldType = int,
            default = 5
        )

        self.scalingAmplitude = Parameter(
            title = "Scaling factor for SO amplitude",
            fieldType = float,
            default = 0.7
        )

        self.scalingNegPeak = Parameter(
            title = "Scaling factor for SO negative peak",
            fieldType = float,
            default = 0.0
        )

        self.percentile = Parameter(
            title = "Percentage of SOs to keep [%]",
            fieldType = float,
            default = 65
        )

    def compute(self, signal):

        intervals = signal.findWaves()

        def isEvent(interval):

            currSignal = signal.data[interval[0]:interval[1]]

            currDuration = interval[1] - interval[0]

            minInd = np.where(currSignal == np.min(currSignal))[0]
            maxInd = np.where(currSignal == np.max(currSignal))[0]

            firstCrossToMinDuration = minInd
            minToMaxDuration = maxInd - minInd
            maxToSecondCrossDuration = len(currSignal) - maxInd

            posPeaks, _ = find_peaks(signal.data[interval[0]:interval[1]], height=0)
            nPosPeaks = len(posPeaks)

            if self.durationLow * signal.samplingRate <= currDuration <= self.durationHigh * signal.samplingRate and \
                firstCrossToMinDuration <= self.firstCrosstoMinDuration * signal.samplingRate and \
                minToMaxDuration <= self.minToMaxDuration * signal.samplingRate and \
                maxToSecondCrossDuration <= self.maxToSecondZeroCrossDuration * signal.samplingRate and \
                nPosPeaks <= self.nPosPeaks:

                return True

            return False

        return np.array([interval for interval in intervals if isEvent(interval)])

    def filter(self, events, data):

        if self.scalingAmplitude:

            amplitudes = [ event.maxVoltage - event.minVoltage for event in events ]

            amplitudeThreshold = np.mean(amplitudes) * self.scalingAmplitude

            events = [ event for event in events if (event.maxVoltage - event.minVoltage) >= amplitudeThreshold ]

        if self.scalingNegPeak:

            negAmplitudes = [ event.minVoltage for event in events ]

            negThreshold = np.mean(negAmplitudes) * self.scalingNegPeak

            events = [ event for event in events if event.minVoltage <= negThreshold ]

        
        amplitudes = [ event.maxVoltage - event.minVoltage for event in events ]

        amplitudeThreshold = np.percentile(amplitudes, 100 - self.percentile)

        events = [ event for event in events if (event.maxVoltage - event.minVoltage) >= amplitudeThreshold ]

        return events
