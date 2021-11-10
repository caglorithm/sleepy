
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter

class Massimi(Algorithm):

    def __init__(self):

        self.name = "Massimini (2004)"

        self.negativeHeight = Parameter(
            title = "Required height of negative peak (-μV)",
            fieldType = float,
            default = 40.0
        )

        self.negativeToPositivePeak = Parameter(
            title = "Negative-To-Positive peak (μV)",
            fieldType = float,
            default = 70.0
        )

        self.separation = Parameter(
            title = "Separation of zero-crossings (seconds)",
            fieldType = float,
            default = 0.3
        )

    def compute(self, signal):
        """Make computations on epoch level
        """

        def isEvent(peak):

            valley = signal.findValley(peak)

            if valley:
                if valley.negativeToPositivePeak > self.negativeToPositivePeak:
                    if  valley.separation >= self.separation * signal.samplingRate:
                        return True

            return False

        negativePeaks = signal.getNegativePeaks(self.negativeHeight)

        return list(filter(isEvent, negativePeaks))
