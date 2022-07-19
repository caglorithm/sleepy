from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

spec = [
        ('nil', int32),               
        ('capacity', int32),
        ('distance', float32[:]),
        ('dataIndex', int32[:]),
        ('lastElement', int32),
        ('topDistance', float32),
        ('topDataIndex', int32)
]

@jitclass(spec)
class MaxPriorityQueue:

    def __init__(self, c):
        self.nil = -100
        self.capacity = c + 1
        self.distance = np.zeros(self.capacity, dtype = float32)
        self.dataIndex = np.zeros(self.capacity, dtype = int32)
        self.lastElement = 0
        self.topDistance = 0.0
        self.topDataIndex = 0

    def insert(self, d, i):

        if self.lastElement < self.capacity - 1:
            self.lastElement += 1
        else:
            print("Error: queue is full!")
            return

        # Insert to the last element
        self.distance[self.lastElement] = d
        self.dataIndex[self.lastElement] = i

        # Go through the queue to make sure that the top is maximum
        B = self.lastElement
        A = int(B / 2)

        while B > 1 and self.distance[A] < self.distance[B]:
            self.swap(B, A)
            B = A
            A = int(B / 2)

    def pop(self):

        if self.lastElement == 0:
            print("Error: queue is empty!")
            return

        # Get dequeued data
        self.topDistance = self.distance[1]
        self.topDataIndex = self.dataIndex[1]

        # Swap last and first data
        self.swap(1, self.lastElement)

        # Remove last data
        self.distance[self.lastElement] = -1
        self.dataIndex[self.lastElement] = -1

        self.lastElement -= 1

        # Go through the queue to make sure that the top is maximum
        A = 1
        B = 2*A
        while B <= self.lastElement:
            if B + 1 <= self.lastElement and self.distance[B+1] > self.distance[B]:
                B += 1

            if self.distance[A] >= self.distance[B]:
                break

            self.swap(A, B)
            A = B
            B = 2*A

    def swap(self, A, B):

        tempDist = self.distance[A]
        tempIndex = self.dataIndex[A]

        self.distance[A] = self.distance[B]
        self.dataIndex[A] = self.dataIndex[B]

        self.distance[B] = tempDist
        self.dataIndex[B] = tempIndex

    def firstDistance(self):
        if self.isEmpty():
            return np.inf
        else:
            return self.distance[1]

    def firstDataIndex(self):
        if self.isEmpty():
            return self.nil
        else:
            return self.dataIndex[1]

    def isEmpty(self):
        return self.lastElement == 0

    def isFull(self):
        return self.lastElement == self.capacity - 1

