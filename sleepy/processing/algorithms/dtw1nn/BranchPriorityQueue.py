from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import deferred_type
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

from .Tree import Tree
TreeType = deferred_type()
TreeType.define(Tree.class_type.instance_type)
spec = [            
    ('capacity', int32),
    ('distance', float32[:]),
    ('data', types.ListType(Tree.class_type.instance_type)),      
    ('lastElement', int32),
    ('topDistance', float64),
    ('topData', TreeType), 
    ('topDataIndex', int32)
]
@jitclass(spec)
class BranchPriorityQueue:

    def __init__(self, c):

        self.capacity = c + 1
        self.distance = np.zeros(self.capacity, dtype = float32)
        self.data = typed.List.empty_list(item_type=Tree(None)) 
        for i in range(self.capacity):
            self.data.append(Tree(None))
        self.lastElement = 0
        self.topDistance = 0.0
        self.topData = Tree(None) 
        self.topDataIndex = -100

    def insert(self, d, t):
        if self.lastElement < self.capacity - 1:
            self.lastElement += 1
        else:
            print("Error: queue is full!")
            return

        self.distance[self.lastElement] = d
        self.data[self.lastElement] = t

        B = self.lastElement
        A = int(B / 2)
        while B > 1 and self.distance[A] > self.distance[B]:
            self.swap(B, A)
            B = A
            A = int(B / 2)

    def pop(self):
        if self.lastElement == 0:
            print("Error: queue is full!")
            return

        self.topDistance = self.distance[1]
        self.topData = self.data[1]

        self.swap(1, self.lastElement)

        self.distance[self.lastElement] = -1
        self.data.pop(self.lastElement)

        self.lastElement -= 1

        A = 1
        B = 2*A
        while B <= self.lastElement:
            if B + 1 <= self.lastElement and self.distance[B+1] < self.distance[B]:
                B += 1

            if self.distance[A] <= self.distance[B]:
                break

            self.swap(A, B)
            A = B
            B = 2*A

        return self.topData

    def swap(self, A, B):

        tempDist = self.distance[A]
        tempData = self.data[A]

        self.distance[A] = self.distance[B]
        self.data[A] = self.data[B]

        self.distance[B] = tempDist
        self.data[B] = tempData

    def isEmpty(self):

        return self.lastElement == 0

    def firstDistance(self):
        if self.isEmpty():
            return np.inf
        else:
            return self.distance[1]
