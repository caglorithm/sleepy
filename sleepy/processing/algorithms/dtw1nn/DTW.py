from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import typed, types
from numba.types import pyobject
import numpy as np
spec = [
        ('maxSeqLen', int32),               
        ('D', float64[:,:]),
        ('distComputation', float64)
]
@jitclass(spec)
class DTW:

    def __init__(self):

        maxSeqLen = 15000
        self.D = np.zeros((maxSeqLen, maxSeqLen), dtype = float64)
        self.distComputation = 0.0

    def dtw(self, Q, C, W):

        """
        Function for calculating dynamic time warping instance.
        Input parameters:
        Q - query time series 1 x N
        C - comparison time series 1 x M
        W - warping window
        """

        nq = len(Q) # length of query
        nc = len(C) # length of comparison
        w = np.max(np.array([W, np.absolute(nq - nc)])) # warping window

        mq = np.min(np.array([nq, 1 + w])) # boundary of cost matrix
        mc = np.min(np.array([nc, 1 + w]))

        self.D[0][0] = np.power((Q[0] - C[0]), 2)
        self.distComputation = 1

        for i in range(1, mq):
            self.D[i][0] = self.D[i-1][0] + np.power((Q[i] - C[0]), 2)

        if i < nq:
            self.D[i][0] = np.inf

        for j in range(1, mc):
            self.D[0][j] = self.D[0][j-1] + np.power((Q[0] - C[j]), 2)

        if j < nc:
            self.D[0][j] = np.inf

        self.distComputation += (mq + mc)

        for i in range(1, nq):
            jStart = np.max(np.array([1, i - w]))
            jStop = np.min(np.array([nc, i + w + 1]))

            for j in range(jStart, jStop):

                cost = np.power((Q[i] - C[j]), 2)
                temp = np.min(np.array([self.D[i - 1][j - 1], self.D[i - 1][j], self.D[i][j - 1]]))
                self.D[i][j] = cost + temp
                self.distComputation += 1

            if jStop < nc:
                self.D[i][jStop] = np.inf

            if i < nq - 1:
                self.D[i+1][jStart] = np.inf


        return self.D[nq-1][nc-1]
