from numba import deferred_type, int64, boolean, types, float64, int32, optional
from numba.experimental import jitclass
import numpy as np

TreeType = deferred_type()
spec = [
        ('children', optional(TreeType)),
        ('dataIndex', int64[:]),
        ('dataClass', int64[:]),
        ('dataLabel', int64[:]),
        ('thisIsLeaf', boolean),
        ('thisIsRoot', boolean),
        ('centroid', types.List(float64, reflected=False)),
        ('centroidLabel', int32)
]
@jitclass(spec)
class TreeBase:

    def __init__(self):
        self.children = None
        self.dataIndex = np.empty(0, dtype = int64)
        self.dataClass = np.empty(1, dtype = int64)
        self.dataLabel = np.empty(1, dtype = int64)
        self.thisIsLeaf = False
        self.thisIsRoot = False
        self.centroid = [ float64(x) for x in range(0) ]
        self.centroidLabel = -100

    def createLeaf(self, dataIndex, dataClass):
        self.thisIsLeaf = True
        self.dataIndex = dataIndex
        self.dataClass = np.array(dataClass, dtype = int64)

    def createNonLeaf(self, centroid, dataLabel, dataIndex):

        self.centroid = centroid
        self.dataLabel = np.array(dataLabel, dtype = int64)
        self.dataIndex = dataIndex 
        if len(dataIndex) > 0:
            self.centroidLabel = self.mode()    

    def isLeaf(self):
        return self.thisIsLeaf

    def leafSize(self):
        return np.shape(self.dataIndex)[0]

    def setRoot(self):
        self.thisIsRoot = True

    def mode(self):

        count = np.bincount(self.dataLabel)
        return np.argmax(count)




TreeType = deferred_type()

spec = [
    ('parent', optional(TreeType)),
    ('left_child', optional(TreeType)),
    ('right_child', optional(TreeType)),
    ('sibling', optional(TreeType)),
    ('dataIndex', int64[:]),
    ('dataClass', int64[:]),
    ('dataLabel', int64[:]),
    ('thisIsLeaf', boolean),
    ('thisIsRoot', boolean),
    ('centroid', float64[:]),
    ('centroidLabel', int32)
]
@jitclass(spec)
class Tree:
    def __init__(self, parent):

        self.parent = parent
        # initialize parent and left right children as None
        self.left_child = None
        self.right_child = None
        self.sibling = None
        if parent is not None:
            parent.add_child(self)

        self.dataIndex = np.empty(0, dtype = int64)
        self.dataClass = np.empty(1, dtype = int64)
        self.dataLabel = np.empty(1, dtype = int64)
        self.thisIsLeaf = False
        self.thisIsRoot = False
        self.centroid = np.empty(1)
        self.centroidLabel = -100

    @property
    def children(self):
        """ A list with all children. """
        children = []
        child = self.left_child
        while child is not None:
            children.append(child)
            child = child.sibling
        return children

    def add_sibling(self, sibling):
        self.sibling = sibling

    def add_child(self, child):
        # if parent has no children
        if self.left_child is None:
            # this node is it first child
            self.left_child = child
            self.right_child = child
        else:
            # the last (now right) child will have this node as sibling
            self.right_child.add_sibling(child)
            self.right_child = child

    def createLeaf(self, dataIndex, dataClass):
        self.thisIsLeaf = True
        self.dataIndex = dataIndex 
        self.dataClass = np.array(dataClass, dtype = int64)

    def createNonLeaf(self, centroid, dataLabel, dataIndex):

        self.centroid = centroid
        self.dataLabel = np.array(dataLabel, dtype = int64)
        self.dataIndex = dataIndex 
        if len(dataIndex) > 0:
            self.centroidLabel = self.mode()    

    def isLeaf(self):
        return self.thisIsLeaf

    def leafSize(self):
        return np.shape(self.dataIndex)[0]

    def setRoot(self):
        self.thisIsRoot = True

    def mode(self):

        count = np.bincount(self.dataLabel)
        return np.argmax(count)

    def addChild(self, node):
        return self.children.append(node)
TreeType.define(Tree.class_type.instance_type)
