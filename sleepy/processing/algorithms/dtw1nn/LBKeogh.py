from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat
spec = [
        ('distComputation', int32)
]
@jitclass(spec)
class LBKeogh:

    def __init__(self):
        self.distComputation = 0

    def envelope(self, query, w):

        wedge = np.empty((2, np.shape(query)[0]), dtype=float64)
        wedge[0] = np.empty(np.shape(query)[0], dtype=float64)
        wedge[0][0:len(query)] = -np.inf
        wedge[1] = np.empty(len(query), dtype=float64)
        wedge[1][0:len(query)] = np.inf
        for i in range(0, len(query)):
            
            jStart = 0 if i - w < 0 else i-w
            jStop = len(query) if i + w + 1 > len(query) else i + w + 1

            for j in range(jStart, jStop):
                wedge[0][i] = np.max(np.array([wedge[0][i], query[j]]))
                wedge[1][i] = np.min(np.array([wedge[1][i], query[j]]))


        self.distComputation = len(query)

        return wedge

    def compute(self, wedge, candidate):

        minLength = np.min(np.array([len(wedge[0]), len(candidate)]))
        res = 0

        for i in range(0, minLength):

            if candidate[i] < wedge[1][i]:

                res += np.power((wedge[1][i] - candidate[i]), 2)

            elif wedge[0][i] < candidate[i]:

                res += np.power((wedge[0][i] - candidate[i]), 2)

        self.distComputation = minLength

        return res
