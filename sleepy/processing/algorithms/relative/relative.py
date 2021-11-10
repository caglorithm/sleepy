
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class Relative(Algorithm):

	def __init__(self):

		self.name = "Relative Amplitude"

		self.durationLow = Parameter(
			title = "Lower bound for duration interval [sec]",
			fieldType = float,
			default = 0.9
		)

		self.durationHigh = Parameter(
			title = "Higher bound for duration interval [sec]",
			fieldType = float,
			default = 2.0
		)

		self.scalingAmplitude = Parameter(
			title = "Scaling factor for SO amplitude",
			fieldType = float,
			default = 2/3
		)

		self.scalingNegPeak = Parameter(
			title = "Scaling factor for SO negative peak",
			fieldType = float,
			default = 2/3
		)

	def compute(self, signal):

		intervals = signal.findWaves()

		def isEvent(interval):

			currDuration = interval[1] - interval[0]

			if self.durationLow * signal.samplingRate <= currDuration <= self.durationHigh * signal.samplingRate:
						
				return True
			
			return False

		return np.array([ interval for interval in intervals if isEvent(interval) ])

	def filter(self, events, data):

		amplitudes = [ event.maxVoltage - event.minVoltage for event in events ]

		amplitudeThreshold = np.mean(amplitudes) * self.scalingAmplitude

		negAmplitudes = [ event.minVoltage for event in events ]

		negThreshold = np.mean(negAmplitudes) * self.scalingNegPeak

		return [ event for event in events if event.minVoltage <= negThreshold and \
				(event.maxVoltage - event.minVoltage) >= amplitudeThreshold ]
