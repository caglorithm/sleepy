
class Valley:

    def __init__(self, nCrossing, pCrossing, peak, nextPeak, data):

        self.nCrossing = nCrossing
        self.pCrossing = pCrossing
        self.peak = peak
        self.nextPeak = nextPeak
        self.data = data

    @property
    def separation(self):

        return self.pCrossing - self.nCrossing

    @property
    def negativeToPositivePeak(self):

        return self.data[self.nextPeak] - self.data[self.peak]
