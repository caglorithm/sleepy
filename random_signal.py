
from sleepy.test.data import TestSignal
from sleepy.processing.engine import Engine
from sleepy.processing.algorithms.massimi import Massimi
from sleepy.processing.filters.bandpass.core import BandPassFilter

# Prepare the algorithm and filter instances (we keep the standard values)
algorithm = Massimi().render()
filter = BandPassFilter().render()

# Create a dataset providing the necessary interface to use it in the Engine API
dataset = TestSignal.generateDataset(scale = 2, numberOfSamples = 300, size=50)

# Run the engine API with the given dataset and return a list of events
detected = Engine.run(algorithm, filter, dataset)
print(detected)
