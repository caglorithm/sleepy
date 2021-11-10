
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class Percentile(Algorithm):

    def __init__(self):

        self.name = "Percentile Algorithm"

        self.durationLow = Parameter(
            title = "Lower bound for duration interval [sec]",
            fieldType = float,
            default = 0.8
        )

        self.durationHigh = Parameter(
            title = "Upper bound for duration interval [sec]",
            fieldType = float,
            default = 2.0
        )

        self.percentile = Parameter(
            title = "Percentage of potential SOs to keep [%]",
            fieldType = float,
            default = 25
        )

    def compute(self, signal):

        intervals = signal.findWaves()

        def isEvent(interval):

            currDuration = interval[1] - interval[0]

            if self.durationLow * signal.samplingRate <= currDuration <= self.durationHigh * signal.samplingRate:

                return True

            return False

        return np.array([interval for interval in intervals if isEvent(interval)])

    def filter(self, events, data):

        amplitudes = [ event.maxVoltage - event.minVoltage for event in events ]

        amplitudeThreshold = np.percentile(amplitudes, 100 - self.percentile)

        return [event for event in events if (event.maxVoltage - event.minVoltage) >= amplitudeThreshold ]