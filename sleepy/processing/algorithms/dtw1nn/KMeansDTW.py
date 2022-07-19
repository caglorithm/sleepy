from numba import njit, jit, objmode
from numba.experimental import jitclass
from numba import int32, int64, float32, float64, boolean
from numba import deferred_type
from numba import typed, types
from numba.types import pyobject
import numpy as np
from scipy.io import loadmat, savemat

from .DTW import DTW
from .LBKeogh import LBKeogh
from .DBA import DBA

dtw_type = deferred_type()
dtw_type.define(DTW.class_type.instance_type)
lbkeogh_type = deferred_type()
lbkeogh_type.define(LBKeogh.class_type.instance_type)
dba_type = deferred_type()
dba_type.define(DBA.class_type.instance_type)
spec = [
        ('nil', int32),               
        ('clusterSeed', int32[:]),    
        ('dtw', dtw_type),
        ('lbKeogh', lbkeogh_type),
        ('dba', dba_type)
]
@jitclass(spec)
class KMeansDTW:

    def __init__(self):
        self.nil = -100
        self.clusterSeed = np.empty(1, dtype=int32)
        self.dtw = DTW() 
        self.lbKeogh = LBKeogh()
        self.dba = DBA()

    def kmeanspp(self, K, data, w, centroidIndex, clusterSeed):
        try:
            dummy = len(data[0])
            dataSize = len(data)
        except:
            dataSize = 1


        centroids = [[float64(i) for i in range(0)] for _ in range(K)]
        dist2NearCentroid = np.empty(dataSize, dtype=float64) 
        taken = np.full(dataSize, False, dtype=boolean)
        cluster = 0 # Cluster label
        centroidCount = 1 # Number of centroids found so far


        # Choose first centroid index at random
        firstCentroidIndex = np.random.randint(dataSize) 
        firstCentroid = data[firstCentroidIndex]
        centroids[int32(centroidCount-1)] = list(firstCentroid)
        centroidIndex[int32(centroidCount-1)] = firstCentroidIndex
        clusterSeed[firstCentroidIndex] = cluster
        taken[firstCentroidIndex] = True

        # Cluster the data around the first centroid, store the distances
        for i in range(dataSize): 
            if boolean(i != firstCentroidIndex):
                dist2NearCentroid[i] = self.dtw.dtw(firstCentroid, data[i], w)
                clusterSeed[i] = cluster

        # Continue to find the remaining centroids
        while centroidCount < K:
            nextCentroidIndex = self.nil #Index to the next centroid
            distSum = [] # Cumulative distance

            # Calculating the cumulative sum of the distance to the next centroid
            distSum.append(dist2NearCentroid[0])

            for i in range(1, dataSize): 
                if not taken[i]:
                    distSum.append(distSum[i-1] + dist2NearCentroid[i])
                else:
                    distSum.append(0.0)


            # Pick a random number between 0 and cumulative distance
            r = np.random.rand(1) * distSum[-1]

            # Find the next centroid index when sum >= r
            for i in range(dataSize):
                if not taken[i]:
                    if distSum[i] >= r:
                        nextCentroidIndex = i
                        break

            # Pick the last available point
            if nextCentroidIndex == self.nil:
                for i in range(dataSize - 1, -1, -1):
                    if not taken[i]:
                        nextCentroidIndex = i
                        break

            if nextCentroidIndex != self.nil:
                # Pick the next centroid from the data set
                nextCentroid = data[nextCentroidIndex]

                centroids[centroidCount] = list(nextCentroid)
                centroidIndex[centroidCount] = nextCentroidIndex                
                clusterSeed[nextCentroidIndex] = cluster
                cluster = cluster + 1
                taken[nextCentroidIndex] = True

                if centroidCount < K:
                    wedge = self.lbKeogh.envelope(nextCentroid, w)

                    for j in range(dataSize): 
                        if not taken[j]:
                            lbDistance = self.lbKeogh.compute(wedge, data[j])
                            if lbDistance < dist2NearCentroid[j]:
                                dtwDistance = self.dtw.dtw(nextCentroid, data[j], w)

                                if dtwDistance < dist2NearCentroid[j]:
                                    dist2NearCentroid[j] = dtwDistance
                                    clusterSeed[j] = cluster

                centroidCount += 1
            else:
                break


        return centroids, centroidIndex, clusterSeed



    def compute(self, K, data, dataClass, dataIndex,\
                                    w, I_max, nbDataInClusters, clusterIndex):
        """
        Function to compute centroids of cluster (?)
        """
        try:
            dummy = len(data[0])
            dataSize = len(data)
        except:
            dataSize = 1
        centroidIndex = np.empty(K, dtype=int32)
        clusterSeed = np.empty(dataSize, dtype=int32)

        # Initialize k-means algorithm using k-means++
        centroids, centroidIndex, clusterSeed = self.kmeanspp(K, data, w, centroidIndex, clusterSeed)
        for i in range(I_max):
            print("Iterations: ", i+1)
            newCentroids, nbDataInClusters, clusterIndex, clusterSeed \
                = self.clusterMean(K, centroids, clusterSeed, data, w, nbDataInClusters, clusterIndex)
            if centroids == newCentroids: 
                break
            else:
                centroids = list(newCentroids)
                clusterSeed = self.clusterAroundCentroids(data, centroids, w, clusterSeed)

        self.clusterSeed = clusterSeed

        return centroids, nbDataInClusters, clusterIndex, clusterSeed


    def clusterMean(self, K, oldCentroids, clusterSeed, data, w, nbDataInClusters, clusterIndex):

        newCentroids = [ [float64(i) for i in range(0)] for _ in range(K) ]
        dataCount = 0 # Iterates over the whole data set
        jStart = 0 # Determines the starting value when finding the clusters around centroids


        # Go through all the centroids
        for i in range(K):
            clusterSize = 0

            try:
                dummy = len(data[0])
                dataSize = len(data)
            except:
                dataSize = 1

            for j in range(dataSize):
                if clusterSeed[j] == i:   
                    clusterIndex[dataCount] = j 
                    dataCount += 1
                    clusterSize += 1

            # If there is data in that cluster
            if clusterSize > 0:
                # Store the data count for references later
                nbDataInClusters[i] = clusterSize 

                clusterCount2 = 0
                cluster =  [ [float64(i) for i in range(0)] for _ in range(clusterSize) ]

                for j in range(jStart, jStart + clusterSize):
                    cluster[clusterCount2] = list(data[int(clusterIndex[j])])
                    clusterCount2 += 1

                jStart += clusterSize

                interim = self.dba.compute(oldCentroids[i], cluster, 10, w)
                print("i", i, "cluster size: ", len(cluster))
                if len(interim):
                    newCentroids[i] = list(interim) 
                else:
                    newCentroids[i] = [np.nan] 
                    nbDataInClusters[i] = 0
            else:
                nbDataInClusters[i] = 0
                newCentroids[i] = [np.nan] 

        return newCentroids, nbDataInClusters, clusterIndex, clusterSeed


    def clusterAroundCentroids(self, data, centroids, w, clusterSeed):
        try:
            dummy = len(data[0])
            dataSize = len(data)
        except:
            dataSize = 1

        for i in range(dataSize):
            wedge = self.lbKeogh.envelope(data[i], w)

            # LB-Keogh NN-DTW
            bestSoFar = np.inf
            for j in range(len(centroids)):
                if not np.isnan(np.array(centroids[j]))[0]: 
                    lbDistance = self.lbKeogh.compute(wedge, centroids[j])
                    if lbDistance < bestSoFar:
                        dtwDistance = self.dtw.dtw(centroids[j], data[i], w)
                        if dtwDistance < bestSoFar:
                            bestSoFar = dtwDistance
                            clusterSeed[i] = j

        return clusterSeed

