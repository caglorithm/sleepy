from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import deferred_type
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

from .utils import argMin3
spec = [
    ('maxSeqLen', int32),               
    ('NIL', int32),
    ('DIAGONAL', int32),
    ('UP', int32),
    ('LEFT', int32),
    ('costMatrix', float64[:,:]),
    ('pathMatrix', int32[:,:]),
    ('optimalPathLength', int32[:,:])
]
@jitclass(spec)
class DBA:

    def __init__(self):
        maxSeqLen = 1500
        self.NIL = -1
        self.DIAGONAL = 0
        self.UP = 2
        self.LEFT = 1
        self.costMatrix = np.empty((maxSeqLen, maxSeqLen), dtype = float64)
        self.pathMatrix = np.empty((maxSeqLen, maxSeqLen), dtype = int32)
        self.optimalPathLength = np.empty((maxSeqLen, maxSeqLen), dtype = int32)

    def update(self, C, sequences, w):
        tupleAssociation = [ [ float64(x) for x in range(0)] for _ in range(np.shape(C)[0]) ]

        res = 0.0
        centerLength = len(C)        

        for T in sequences: 
                            
            seqLength = len(T)                

            self.costMatrix[0][0] = np.power((C[0] - T[0]), 2)
            self.pathMatrix[0][0] = self.NIL
            self.optimalPathLength[0][0] = 0
            distComputation = 1

            for i in range(1, np.min(np.array([centerLength, 1 + w]))):
                self.costMatrix[i][0] = self.costMatrix[i - 1][0] + \
                                        np.power((C[i] - T[0]), 2)
                self.pathMatrix[i][0] = self.UP
                self.optimalPathLength[i][0] = i

            if i < centerLength:
                self.costMatrix[i][0] = np.inf

            for j in range(1, np.min(np.array([seqLength, 1 + w]))):
                self.costMatrix[0][j] = self.costMatrix[0][j - 1] + \
                                        np.power((T[j] - C[0]), 2)
                self.pathMatrix[0][j] = self.LEFT
                self.optimalPathLength[0][j] = j

            if j < seqLength:
                self.costMatrix[0][j] = np.inf

            distComputation += (np.min(np.array([centerLength, 1 + w])) + np.min(np.array([seqLength, 1 + w])))

            for i in range(1, centerLength):
                jStart = np.max(np.array([1, i - w]))
                jStop = np.min(np.array([seqLength, i + w + 1]))

                for j in range(jStart, jStop):
                    indiceRes = argMin3(self.costMatrix[i - 1][j - 1], \
                                        self.costMatrix[i][j - 1], \
                                        self.costMatrix[i - 1][j])
                    self.pathMatrix[i][j] = indiceRes

                    if indiceRes == self.DIAGONAL:
                        res = self.costMatrix[i - 1][j - 1]
                        self.optimalPathLength[i][j] = self.optimalPathLength[i - 1][j - 1] + 1
                    elif indiceRes == self.LEFT:
                        res = self.costMatrix[i][j - 1]
                        self.optimalPathLength[i][j] = self.optimalPathLength[i][j - 1] + 1
                    elif indiceRes == self.UP:
                        res = self.costMatrix[i - 1][j]
                        self.optimalPathLength[i][j] = self.optimalPathLength[i - 1][j] + 1

                    self.costMatrix[i][j] = res + np.power((C[i] - T[j]), 2)
                    distComputation += 1

                if jStop < seqLength:
                    self.costMatrix[i][jStop] = np.inf

                if i < centerLength - 1:
                    self.costMatrix[i + 1][jStart] = np.inf

            a = np.array([self.optimalPathLength[centerLength-1][seqLength-1],\
                                        self.optimalPathLength[seqLength-1][centerLength-1],\
                                        self.optimalPathLength[centerLength-1][centerLength-1],\
                                        self.optimalPathLength[seqLength-1][seqLength-1]])
            
            nonzero_a = a[np.nonzero(a)]
            nbTuplesAverageSeq = np.min(nonzero_a)
            

            i = centerLength - 1
            j = seqLength - 1

            for t in range(nbTuplesAverageSeq - 1, -1, -1):
                tupleAssociation[i].append(T[j]) 

                if self.pathMatrix[i][j] == self.DIAGONAL:
                    i = i - 1
                    j = j - 1
                elif self.pathMatrix[i][j] == self.LEFT:
                    j = j - 1
                elif self.pathMatrix[i][j] == self.UP:
                    i = i - 1
        c = np.zeros(centerLength)
        for t in range(centerLength):
            c[t] = self.barycenter(tupleAssociation[t])
        return list(c)

    def barycenter(self, tab):

        if len(tab) < 1:
            return 0.0 

        s = 0.0
        for o in tab:
            s += o

        return s / len(tab)

    def compute(self, T, sequences, I_max, w):
        for i in range(I_max):
            T = self.update(T, sequences, w)

        return T


