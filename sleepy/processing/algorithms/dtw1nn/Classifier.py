from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean, prange
from numba import deferred_type
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

from .KMeansDTW import KMeansDTW
from .Tree import Tree
from .MaxPriorityQueue import MaxPriorityQueue
from .BranchPriorityQueue import BranchPriorityQueue
from .MinPriorityQueue import MinPriorityQueue
from .LBKeogh import LBKeogh
from .DTW import DTW
from .utils import sort
import time

kmeansdtw_type = deferred_type()
kmeansdtw_type.define(KMeansDTW.class_type.instance_type)

TreeType = deferred_type()
TreeType.define(Tree.class_type.instance_type)
maxprior_type = deferred_type()
maxprior_type.define(MaxPriorityQueue.class_type.instance_type)
branch_type = deferred_type()
branch_type.define(BranchPriorityQueue.class_type.instance_type)
lbkeogh_type = deferred_type()
lbkeogh_type.define(LBKeogh.class_type.instance_type)
dtw_type = deferred_type()
dtw_type.define(DTW.class_type.instance_type)

spec = [            
    ('trainingDataset', types.List(float64[::1], reflected=True)),
    ('trainingDatasetClass', types.List(int32, reflected=True)),
    ('trainingDatasetSize', int64),        
    ('maxPQSize', int32),
    ('nil', int32),
    ('branchFactor', int32),
    ('nTimeSeriesInCluster', int32),
    ('nbTimeSeriesToExamine', int32),
    ('nearestNeighbour', int32),
    ('intervals', int32),
    ('distComputation', float64),
    ('distComputationPerQuery', float64),
    ('nbTimeSeriesSeen', int32),
    ('nbTimeSeriesToActualNN', int32),
    ('timeToActualNN', float64),
    ('nnIndex', int32),
    ('levels', int32),
    ('kNNIndex', maxprior_type),
    ('dtwBranchPQ', branch_type),
    ('lbBranchPQ', branch_type), 
    ('lbKeogh', lbkeogh_type),
    ('parent', TreeType), 
    ('dtw', dtw_type),
    ('kmeans', kmeansdtw_type),
    ('startTime', float64),
    ('stopTime', float64),
    ('saveTime', float64),
    ('elapsedTime', float64),
    ('totalQueryTime', float64),
    ('steps', int32),
    ('precisionSoFar', float64),
    ('errorSoFar', float64),
    ('averageQueryTime', float64),
    ('precision', int32),
    ('actualClass', int64),
    ('index1NN', int32[:]),
    ('errorPerQuery', float64[:]),
    ('preError', float64[:]),
    ('preTime', float64[:]),
    ('preDist', float64[:]),
    ('preErrorAll', types.List(float64)),
    ('preTimeAll', types.List(float64)),
    ('preDistAll', types.List(float64)),
    ('averagePrecisionPerQuery', float64[:]), 
    ('averageErrorPerQuery', float64[:]), 
    ('averageDistPerQuery', float64[:]), 
    ('averageTimePerQuery', float64[:]), 
    ('precisionPerQuery', float64[:]), 
    ('timePerQuery', float64[:]), 
    ('distPerQuery', float64[:]), 
    ('seenSoFarPerQuery', int32[:]),
    ('arrayCount', int32),
    ('maxCount', int32)
]
@jitclass(spec)
class classifierTSI:

    def __init__(self, data, dataClass, K, CT, L, k):
        self.trainingDataset = data
        self.trainingDatasetClass = dataClass
        self.trainingDatasetSize = len(data)

        self.maxPQSize = 1000000 # Maximum size for priority queue
        self.nil = -100 # Constant for not available
        self.branchFactor = K
        self.nTimeSeriesInCluster = CT
        self.nbTimeSeriesToExamine = L # Number of time series to examine
        self.nearestNeighbour = k
        self.intervals = 100 #stepSize 

        self.distComputation = 0.0
        self.distComputationPerQuery = 0.0

        self.nbTimeSeriesSeen = 0

        self.nbTimeSeriesToActualNN = self.nil
        self.timeToActualNN = float64(self.nil)
        self.nnIndex = self.nil

        self.levels = self.nil # Tree level

        self.kNNIndex = MaxPriorityQueue(self.nearestNeighbour)
        self.dtwBranchPQ = BranchPriorityQueue(0) 
        self.lbBranchPQ = BranchPriorityQueue(0) 
        self.lbKeogh = LBKeogh()
        self.dtw = DTW()
        self.kmeans = KMeansDTW()    
        self.parent = Tree(None) 

        self.startTime = 0.0 # Start, stop, save time per query
        self.stopTime = 0.0
        self.saveTime = 0.0
        self.elapsedTime = 0.0 # Time per query
        self.totalQueryTime = 0.0 # Total time to search

        self.steps = 1 # Steps to record error (1 - record error for each training example)

        self.precisionSoFar = 0.0 # Precision so far for each test time series
        self.errorSoFar = 0.0 # Error so far for each test time series
        self.averageQueryTime = float64(self.nil)
        self.precision = self.nil # Precision in searching for NN

        self.actualClass = self.nil#[]
        self.index1NN = np.empty(0, dtype = int32)

        # L experiments parameters
        self.errorPerQuery = np.empty(1, dtype = float64)

        self.preError = np.empty(1, dtype = float64)
        self.preTime = np.empty(1, dtype = float64)
        self.preDist = np.empty(1, dtype = float64)
        self.preErrorAll = [0.0]
        self.preTimeAll = [0.0]
        self.preDistAll = [0.0]
        self.averagePrecisionPerQuery = np.empty(0, dtype=float64) 
        self.averageErrorPerQuery = np.empty(0, dtype=float64) 
        self.averageDistPerQuery = np.empty(0, dtype=float64)
        self.averageTimePerQuery = np.empty(0, dtype=float64)
        self.precisionPerQuery = np.empty(0, dtype=float64)
        self.timePerQuery = np.empty(0, dtype = float64) 
        self.distPerQuery = np.empty(0, dtype = float64)
        self.seenSoFarPerQuery = np.empty(0, dtype = int32)
        self.arrayCount = 0 # Counter for seen so far
        self.maxCount = 0 

    def build_tree(self, data, dataClass, dataIndex, I_max, w):

        """
        :param data: time series dataset; list: N (number of elements) x T (length of each element)
        :param dataClass: labels for each time series; list: N (number of elements) x 1
        :param K: branching factor
        :param I_max: maximum k-means iterations
        :param w: warping window
        """

        self.parent.createLeaf(dataIndex, dataClass)
        stack = typed.List()
        stack.append((data, dataClass, dataIndex, self.parent))
        nIterSearch = 0 # Max. number of iterations for convergence
        while len(stack) and nIterSearch < 10**3: 

            data = stack[0][0]
            dataClass = stack[0][1]
            dataIndex = stack[0][2]
            node = stack[0][3]
            stack.pop(0)

            nbDataInClusters = np.zeros(self.branchFactor, dtype=int32) # Number of time series in each cluster (actual numbers are appended later)
            clusterIndex = np.zeros(len(data), dtype=int32) # Index of each cluster wrt dataset (also appended later)

            centroids, nbDataInClusters, clusterIndex, clusterSeed = self.kmeans.compute(self.branchFactor, data, dataClass, dataIndex,\
                                        w, I_max, nbDataInClusters, clusterIndex)

            jStart = 0 # Counters to find the data in each cluster

            # Go through all the clusters to build the tree

            for i in range(self.branchFactor):
                cluster = [] 
                clusterClass = []

                # Clustering around the centroids using the clusterIndex wrt to data set found earlier
                jEnd = jStart + nbDataInClusters[i]

                cIndex = np.empty((jEnd - jStart), dtype = int64)
                for j in range(jStart, jEnd):
                    cluster.append(data[clusterIndex[j]]) # Add all the timeseries in that cluster
                    clusterClass.append(dataClass[clusterIndex[j]]) # Class of each timeseries in that cluster
                    cIndex[j - jStart] = dataIndex[clusterIndex[j]]

                jStart = jEnd # set the next start point

                # Create a child, non-leaf, using the centroids
                childNode = Tree(None)


                if not np.isnan(np.array(centroids[i]))[0]:
                    if len(clusterClass):
                        childNode.createNonLeaf(np.array(centroids[i]), clusterClass, cIndex)


                        node.add_child(childNode)

                        if len(cluster) > self.nTimeSeriesInCluster:
                            stack.append((cluster, clusterClass, cIndex, childNode))
                        else:
                            childNode.thisIsLeaf = True
            # Print status
            if self.nbTimeSeriesSeen%1 == 0:
                print("Completed:", self.nbTimeSeriesSeen)

            nIterSearch += 1

        print('number of iterations: ', nIterSearch)
        if nIterSearch >= 10**3:
            print('The algorithm did not converge, the clustering is incomplete.')

        self.nbTimeSeriesSeen += len(data)

        return self.parent

    def search_tree(self, tree, query, L, w):

        self.kNNIndex = MaxPriorityQueue(self.nearestNeighbour) # nn priority queue (max PQ)
        self.dtwBranchPQ = BranchPriorityQueue(self.maxPQSize) # Priority queue for DTW branches (min PQ)
        self.lbBranchPQ = BranchPriorityQueue(self.maxPQSize) # Priority queue for LB branches (min PQ)
        self.distComputationPerQuery = 0.0
        self.arrayCount = 0
        self.nbTimeSeriesSeen = 0

        with objmode(startTime='f8'):
            startTime = time.perf_counter()
        self.startTime = startTime
        self.saveTime = 0.0

        # Compute envelope for query time series and use it to compare to the training data set
        wedge = self.lbKeogh.envelope(query, w)
        self.distComputationPerQuery += self.lbKeogh.distComputation

        # Traverse tree to leaf

        self.traverse_tree(tree, query, wedge, w)
        while (not self.dtwBranchPQ.isEmpty() or not self.lbBranchPQ.isEmpty()) \
                and self.nbTimeSeriesSeen < self.nbTimeSeriesToExamine:
            # While priority queues aren't empty and haven't seen L time series
            minLB = np.inf # Minimum lower bound distance
            minD = np.inf # Minimum dtw distance

            # Update minimum lower-bound and dtw distance
            if not self.lbBranchPQ.isEmpty():
                minLB = self.lbBranchPQ.firstDistance()
            if not self.dtwBranchPQ.isEmpty():
                minD = self.dtwBranchPQ.firstDistance()

            while minLB < minD:
                # If min LB distance is smaller than min dtw distance, compute dtw
                topLBBranch = self.lbBranchPQ.pop() # Min branch from lower-bound PQ
                dtwDistance = self.dtw.dtw(query, topLBBranch.centroid, w)
                self.distComputationPerQuery += self.dtw.distComputation

                self.dtwBranchPQ.insert(dtwDistance, topLBBranch) # Add that branch to dtw PQ

                if not self.lbBranchPQ.isEmpty():
                    minLB = self.lbBranchPQ.firstDistance()
                else:
                    minLB = np.inf
                if not self.dtwBranchPQ.isEmpty():
                    minD = self.dtwBranchPQ.firstDistance()

            if not self.dtwBranchPQ.isEmpty():
                # If dtw queue is not empty, dequeue the first one as the most promising branch to traverse
                N = self.dtwBranchPQ.pop()
                self.traverse_tree(N, query, wedge, w)

        predictClass = self.trainingDatasetClass[self.getNN()] # Predicted class of the query

        return predictClass

    def traverse_tree(self, tree, query, wedge, w):

        stack = []
        stop = True
        while stop:

            if tree.isLeaf():
                stop = False


                # If branch is leaf, add to the nn priority queue
                nodeIndex = tree.dataIndex # Data index of training data set stored in the leaf
                                           
                # Order the time series using a minimum priority queue based on LB distance
                index = np.zeros(np.shape(nodeIndex)[0], dtype=int32)
                lbDistances = np.zeros(np.shape(nodeIndex)[0], dtype = float64)


                for j in range(0, np.shape(nodeIndex)[0]):

                    index[j] = nodeIndex[j]
                    lbDistances[j] = self.lbKeogh.compute(wedge, self.trainingDataset[index[j]])
                    self.distComputationPerQuery += self.lbKeogh.distComputation
                lbDistances, index = sort(lbDistances, index, 0, np.shape(lbDistances)[0] - 1)

                # Apply LB Keogh-NN-DTW with LB Keogh to all the time series in this node
                for j in range(np.shape(nodeIndex)[0]):
                    # Get the worst distance from the result queue
                    worstSoFarDist = self.kNNIndex.firstDistance()

                    if lbDistances[j] < worstSoFarDist:
                        dtwDistance = self.dtw.dtw(query, self.trainingDataset[index[j]], w)

                        self.distComputationPerQuery += self.dtw.distComputation

                        if dtwDistance < worstSoFarDist:
                            # If dtw distance is better than the worst knn distance, add it to the results queue
                            # If result queue is full, pop is and insert
                            if self.kNNIndex.isFull():
                                self.kNNIndex.pop()
                            self.kNNIndex.insert(dtwDistance, index[j])

                    self.nbTimeSeriesSeen += 1

                    self.recordResults() 

                    if self.nbTimeSeriesSeen == self.nbTimeSeriesToExamine:
                            # Stop searching if enough time series have been seen
                            return

            else:
                children = tree.children # List of children nodes
                numCluster = len(children)

                if numCluster > 0:
                    # Find the closest centroid and go there

                    # Order the centroids using a minimum priority queue based on LB distance
                    index = np.zeros(numCluster, dtype=int32)
                    lbDistances = np.zeros(numCluster)
                    for i in range(numCluster):
                        if children[i].centroid is not None:
                            index[i] = i
                            lbDistances[i] = self.lbKeogh.compute(wedge, children[i].centroid) 
                            self.distComputation += self.lbKeogh.distComputation
                            self.distComputationPerQuery += self.lbKeogh.distComputation
                    lbDistances, index = sort(lbDistances, index, 0, np.shape(lbDistances)[0] - 1)

                    bestSoFar = np.inf # Best distance so far
                    distances = np.zeros(numCluster) # Vector for dtw distance
                    dtwFlag = np.zeros(numCluster, dtype=boolean) # Indicator for branches where dtw has been computed
                    nearestIndex = self.nil # Nearest centroid index
                    bestClass = self.nil

                    # Apply LB Keogh-NN-DTW to all the centroids in this node
                    for i in range(numCluster):
                        if lbDistances[i] < bestSoFar:
                            # If lower bound is smaller than the best so far, compute dtw distance
                            if children[i].centroid is not None:
                                dtwDistance = self.dtw.dtw(query, children[i].centroid, w)

                                self.distComputationPerQuery += self.dtw.distComputation
                                distances[index[i]] = dtwDistance
                                dtwFlag[index[i]] = True

                                if dtwDistance < bestSoFar:
                                    # Update nearest candidate if dtw is smaller than best so far
                                    bestSoFar = dtwDistance
                                    nearestIndex = index[i]
                                    bestClass = children[i].centroidLabel


                                # Record results before seeing the first time series
                                self.recordPreResults(bestClass)
                        else:
                            distances[index[i]] = lbDistances[i]

                    if self.nbTimeSeriesSeen < self.nbTimeSeriesToExamine:
                        if children[nearestIndex].centroid is not None:
                            if children[nearestIndex].leafSize() > 0:
                                # Call traverse tree
                                tree = children[nearestIndex]
                                stack.append((children, nearestIndex, distances, dtwFlag))
                            else:
                                if distances[nearestIndex] < self.kNNIndex.firstDistance():
                                    if self.kNNIndex.isFull():
                                        self.kNNIndex.pop()
                                    self.kNNIndex.insert(distances[nearestIndex], children[nearestIndex].dataIndex[0])
                                    self.nbTimeSeriesSeen += 1

                                    self.recordResults()

        while stack:
            children = stack[len(stack) - 1][0]
            nearestIndex = stack[len(stack) - 1][1]
            distances = stack[len(stack) - 1][2]
            dtwFlag = stack[len(stack) - 1][3]
            stack.pop()
            numCluster = len(children)

            for i in range(numCluster):
                if i != nearestIndex:
                    if dtwFlag[i]:
                        if children[i].leafSize() > 0:

                            self.dtwBranchPQ.insert(distances[i], children[i])
                        else:
                            if distances[i] < self.kNNIndex.firstDistance():
                                if children[i].centroid is not None: 
                                    if self.kNNIndex.isFull():
                                        self.kNNIndex.pop()
                                    self.kNNIndex.insert(distances[i], children[i].dataIndex[0])
                                    self.nbTimeSeriesSeen += 1
                                    self.recordResults()

                    else:
                        if children[i].leafSize() > 0:
                            self.lbBranchPQ.insert(distances[i], children[i])
                        else:
                            if distances[i] < self.kNNIndex.firstDistance():
                                if children[i].centroid is not None:
                                    distances[i] = self.dtw.dtw(query, children[i].centroid, w)
                                    if distances[i] < self.kNNIndex.firstDistance():
                                        if self.kNNIndex.isFull():
                                            self.kNNIndex.pop()
                                        self.kNNIndex.insert(distances[i], children[i].dataIndex[0])
                            self.nbTimeSeriesSeen += 1

                            if self.kNNIndex.firstDataIndex() != self.nil:
                                self.recordResults()
                    if self.nbTimeSeriesSeen == self.nbTimeSeriesToExamine:
                            return


    def recordResults(self):

        if self.nbTimeSeriesSeen == 1 or self.nbTimeSeriesSeen == self.trainingDatasetSize or \
            int(self.nbTimeSeriesSeen / self.steps) == 0:
            self.elapsedTime = self.stopTime - self.startTime - self.saveTime
            if self.trainingDatasetClass[self.kNNIndex.firstDataIndex()] != self.actualClass:
                self.errorPerQuery[self.arrayCount] += 1

            if self.timeToActualNN == float(self.nil):
                self.timeToActualNN = self.elapsedTime
                self.nbTimeSeriesToActualNN = self.nbTimeSeriesSeen

            self.timePerQuery[self.arrayCount] += self.elapsedTime 
            self.distPerQuery[self.arrayCount] += self.distComputationPerQuery 
            if self.seenSoFarPerQuery[self.arrayCount] == 0:
                self.seenSoFarPerQuery[self.arrayCount] = self.nbTimeSeriesSeen
            self.arrayCount += 1

        return self

    def recordPreResults(self, bestClass):

        if self.nbTimeSeriesSeen == 0:

            if bestClass != self.actualClass:
                self.preErrorAll.append(1.0) 
            else:
                self.preErrorAll.append(0.0) 

            self.preTimeAll.append(self.elapsedTime) 
            self.preDistAll.append(self.distComputationPerQuery) 

        return self

    def getNN(self):

        if self.kNNIndex is not None and not self.kNNIndex.isEmpty():

            size = self.kNNIndex.lastElement

            results = MinPriorityQueue(size)

            for i in range(size):
                self.kNNIndex.pop()
                results.insert(self.kNNIndex.topDistance, self.kNNIndex.topDataIndex)

            self.nnIndex = results.firstDataIndex()

        return self.nnIndex

    def performance(self, tree, testingDataset, testingDatasetClass, w, testingDatasetIndex):

        wrongCount = 0 # Counting the number of times the predicted class is wrong
        precisionCount = 0 # Counting the number of time the predicted NN is correct

        totTimeToNN = 0.0
        avgTimeToNN = 0.0
        avgNbTimeToNN = 0.0
        totNbToNN = 0

        # Initialize
        self.totalQueryTime = 0.0
        self.index1NN = np.empty(len(testingDataset), dtype = int32)
        self.distComputation = 0

        # Initialize the results for different time intervals
        self.maxCount = 0
        self.precisionPerQuery = np.empty(self.intervals, dtype = float64)
        self.errorPerQuery = np.empty(self.intervals, dtype = float64)
        self.timePerQuery = np.zeros(self.intervals, dtype = float64)
        self.distPerQuery = np.empty(self.intervals, dtype = float64)
        self.seenSoFarPerQuery = np.zeros(self.intervals, dtype = int32)
        self.averagePrecisionPerQuery = np.empty(self.intervals, dtype = float64)
        self.averageErrorPerQuery = np.empty(self.intervals, dtype = float64)
        self.averageTimePerQuery = np.empty(self.intervals, dtype = float64)
        self.averageDistPerQuery = np.empty(self.intervals, dtype = float64)
        tmpTime = np.empty(len(testingDataset), dtype = float64) 
        tmpError = np.empty(len(testingDataset), dtype = float64) 
        tmpDist = np.empty(len(testingDataset), dtype = float64)
        counts = np.empty(len(testingDataset), dtype = int32)

        # Outputs
        predictClass = np.empty(len(testingDataset), dtype = int32)

        # Go through the whole testing set
        for i in prange(len(testingDataset)):

            self.actualClass = testingDatasetClass[i] # Correct class
            self.nbTimeSeriesToActualNN = self.nil
            self.timeToActualNN = float(self.nil)

            predictClass[i] = self.search_tree(tree, testingDataset[i], self.nbTimeSeriesToExamine, w) # Predicted class of the query
            self.totalQueryTime += self.elapsedTime # Update total query time
            self.index1NN[i] = self.getNN() # Predicted nearest neighbour index of the query
            self.distComputation += self.distComputationPerQuery

            # Update error count
            if predictClass[i] != self.actualClass:
                wrongCount += 1

            self.errorSoFar = wrongCount / (i + 1)

            totNbToNN += self.timeToActualNN
            totNbToNN += self.nbTimeSeriesToActualNN


        # Compute error rate, precision, number of dist computations and avg query time per query at different time intervals
        for i in range(self.intervals):                
            self.averagePrecisionPerQuery[i] = self.precisionPerQuery[i] / len(testingDataset)
            self.averageErrorPerQuery[i] = self.errorPerQuery[i] / len(testingDataset)
            self.averageTimePerQuery[i] = self.timePerQuery[i] / len(testingDataset)
            self.averageDistPerQuery[i] = self.distPerQuery[i] / len(testingDataset)
        try:

            self.preError = np.empty(self.maxCount, dtype = float64)
            self.preTime = np.empty(self.maxCount, dtype = float64)
            self.preDist = np.empty(self.maxCount, dtype = float64)
            self.preError[0:self.maxCount] = tmpError[0:self.maxCount]
            self.preDist[0:self.maxCount] = tmpDist[0:self.maxCount]
            self.preTime[0:self.maxCount] = tmpTime[0:self.maxCount]

            # Compute error rate, precision, number of dist. computations and average query time
            errorRate = wrongCount / len(testingDataset)
            self.averageQueryTime = self.totalQueryTime / len(testingDataset)
            self.precision = precisionCount / len(testingDataset)
            self.distComputation = self.distComputation / len(testingDataset)

            avgTimeToNN = totTimeToNN / len(testingDataset)
            avgNbTimeToNN = totTimeToNN / len(testingDataset)

            return errorRate, predictClass, testingDatasetClass, testingDatasetIndex
        except:
            return errorRate, predictClass, testingDatasetClass, testingDatasetIndex
