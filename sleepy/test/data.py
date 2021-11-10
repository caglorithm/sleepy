
import numpy as np
from sleepy.processing.dataset import Dataset

class TestSignal:

    def generate(size = 10, numberOfSamples = 1000, windowSize = 10, scale = 1):
        """Generates a test signal that should come close to a slow-wave signal
        in terms of amplitudes, negative-to-positive zero-crossings and separation.
        Can be used to test algorithms when in lack of an actual dataset.

        :param size: Integer value determining the relative size of the signal.
        A signal is generated from size many waves, each of which is created from a
        random walk in the interval [0,100].

        :param numberOfSamples: The number of samples of each wave.

        :param windowSize: Size of the second parameter to the running mean, i.e.
        window size.

        :param scale: Standard deviation for the random gaussian walk.

        :returns: The x- and y-axis data of the signal
        """

        x = np.linspace(0, 100, numberOfSamples)

        ySignal = np.concatenate([

            TestSignal.__runningMean(TestSignal.__randomWalk(x, scale), windowSize)
                for _ in range(size)

        ])

        xSignal = np.concatenate([

            x + (i * 100) for i in range(size)

        ])

        return xSignal, ySignal

    def generateDataset(size = 10, numberOfSamples = 1000, windowSize = 10, scale = 1):
        """Generates a test signal that should come close to a slow-wave signal
        in terms of amplitudes, negative-to-positive zero-crossings and separation.
        Can be used to test algorithms when in lack of an actual dataset.

        :param size: Integer value determining the relative size of the signal.
        A signal is generated from size many waves, each of which is created from a
        random walk in the interval [0,100].

        :param numberOfSamples: The number of samples of each wave.

        :param windowSize: Size of the second parameter to the running mean, i.e.
        window size.

        :param scale: Standard deviation for the random gaussian walk.

        :returns: A sub-class instance of Dataset, providing the necessary interface to
        integrate the generated data into sleepy.
        """

        xSignal, ySignal = TestSignal.generate(size, numberOfSamples, windowSize, scale)

        class TestDataset(Dataset):

            def __init__(self, raw):

                super().__init__(raw, None)
                self.samplingRate = raw["fs"]

            @property
            def epochs(self):
                return np.array([[0, numberOfSamples * size]])

            @property
            def data(self):
                return np.array([[self.raw["y"]]])

        return TestDataset({
            "x" : xSignal,
            "y" : ySignal,
            "fs" : numberOfSamples
        })

    def __randomWalk(x, scale):
        """Perfroms a random gaussian walk given a linspace x. Taken from
        https://stackoverflow.com/questions/29050164/produce-random-wavefunction.
        """

        y = 0
        result = []

        for _ in x:

            result.append(y)
            y += np.random.normal(scale = scale)

        return np.array(result)

    def __runningMean(x, N):
        """Applies a running mean for a given signal x and a window size N.
        """

        return np.convolve(x, np.ones((N,))/N)[(N-1):]
