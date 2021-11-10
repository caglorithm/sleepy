
from sleepy.test.data import TestSignal
import matplotlib.pyplot as plt

# Create the x- and y-axis data of a signal with std. dev. 2, 300 samples per sub-wave and 50 sub-waves.
x, y = TestSignal.generate(scale = 2, numberOfSamples = 300, size=50)

# Plot the data
plt.plot(x, y)
plt.show()
