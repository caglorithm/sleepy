from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

from .Tree import Tree
from itertools import chain
def flatten(listOfLists):
    "Flatten one level of nesting"
    return chain.from_iterable(listOfLists)

@jit
def argMin3(a,b,c):
    if a < b:
        if a < c:
            return 0
        else:
            return 2
    else:
        if b < c:
            return 1
        else:
            return 2
@jit
def sort(numbers, index, low, high):
    i = low
    j = high

    pivot = numbers[int((low + high) / 2)]

    while i <= j:
        while numbers[i] < pivot:
            i += 1
        while numbers[j] > pivot:
            j -= 1
        if i <= j:
            numbers, index, i, j = swap(numbers, index, i, j)
            i += 1
            j -= 1

    if low < j:
        numbers, index = sort(numbers, index, low, j)
    if i < high:
        numbers, index = sort(numbers, index, i, high)

    return numbers, index

@jit
def swap(numbers, index, i, j):
    tempNum = numbers[i]
    tempIndex = index[i]
    numbers[i] = numbers[j]
    index[i] = index[j]
    numbers[j] = tempNum
    index[j] = tempIndex

    return numbers, index, i, j

def sfd(node, ndict):
    node.parent = ndict["parent"]
    node.dataIndex = ndict["dataIndex"]
    node.dataClass = ndict["dataClass"]
    node.dataLabel = ndict["dataLabel"]
    node.thisIsLeaf = ndict["thisIsLeaf"]
    node.thisIsRoot = ndict["thisIsRoot"]
    node.centroid = ndict["centroid"]
    node.centroidLabel = ndict["centroidLabel"] 

    for idx, child in enumerate(ndict["children"]):
        child_tree = Tree(None)
        sfd(child_tree, child)
        node.add_child(child_tree)
