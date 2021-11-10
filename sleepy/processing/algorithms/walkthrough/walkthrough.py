from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class Walkthrough(Algorithm):

    def __init__(self):
        self.name = "Walkthrough"

        self.alpha = Parameter(
            title = "Integer parameter alpha",
            fieldType = int,
            default = 5
        )

        self.beta = Parameter(
            title = "Floating-point parameter beta",
            fieldType = float,
            default = 1.2
        )

    def compute(self, signal):

        # Declare an inner function that can be used as a filter
        def isEvent(sample):

            # Get the amplitude for a given sample value
            amplitude = signal.data[sample]

            # Returns true if the filter condition is satisfied
            return amplitude > self.alpha and amplitude < self.beta

        signalLength = len(signal.data)

        # List comprehension to filter all the samples that satisfy our filter
        # condition
        return np.array([ sample for sample in range(signalLength) if isEvent(sample) ])

    def filter(self, events, data):

        # Sort the events ascending by amplitude.
        sortedByAmplitude = sorted(events, key = lambda event: event.amplitude )

        # cut off the first 50% of the events
        return sortedByAmplitude[:len(sortedByAmplitude) // 2]
