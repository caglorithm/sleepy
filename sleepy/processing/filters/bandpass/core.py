
from sleepy.processing.processor import Filter
from sleepy.processing.parameter import Parameter
from scipy.signal import butter, filtfilt

class BandPassFilter(Filter):

    def __init__(self):

        self.name = "Bandpass"

        self.lowCutFrequency = Parameter(
            title = "Low cut-off frequency in Hz",
            fieldType = float,
            default = .1
        )

        self.highCutFrequency = Parameter(
            title = "High cut-off frequency in Hz",
            fieldType = float,
            default = 4.0
        )

        self.order = Parameter(
            title = "Order",
            fieldType = int,
            default = 2
        )

    # Implements:
    # https://stackoverflow.com/questions/12093594/how-to-implement-band-pass-butterworth-filter-with-scipy-signal-butter
    def filter(self, data, samplingRate):

        b, a = butter(
            self.order,
            [
                self.lowCutFrequency / (0.5 * samplingRate),
                self.highCutFrequency / (0.5 * samplingRate)
            ],
            btype = "bandpass"
        )

        return filtfilt(b, a, data)
