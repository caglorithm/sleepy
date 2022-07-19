from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
from .Classifier import classifierTSI
from .Tree import Tree
import numpy as np
import csv
from .utils import sfd, flatten
import dill
import multiprocessing
from multiprocessing import Semaphore
from .Simulation import simulation
from numba import float64, int32

import pickle

class DTW1NN(Algorithm):

    def __init__(self):

        self.name = "DTW-1NN"

        # Default parameters, if changed, model needs to be retrained
        self.nCluster = 10
        self.nLeaf = 30
        self.nSeen = 1000

        self.durationLow = Parameter(
            title = "Lower bound for duration interval [sec]",
            fieldType = float,
            default = 0.8
        )

        self.durationHigh = Parameter(
            title = "Upper bound for duration interval [sec]",
            fieldType = float,
            default = 3.5
        )


    def compute(self, signal):

        intervals = signal.findWaves()
        def isEvent(interval):

            currDuration = interval[1] - interval[0]

            if self.durationLow * signal.samplingRate <= currDuration <= self.durationHigh * signal.samplingRate:

                return True

            return False

        intervals = np.array([interval for interval in intervals if isEvent(interval)])

        if not hasattr(self, 'DTW1NN'):
            
            # Set window size to 10% of max training SO length (in data points)
            windowSize = 119

            # Load data set based on which the classification will be made
            X_train = []
            with open('./sleepy/processing/algorithms/dtw1nn/TrainingDataSamples.csv', 'r') as f:
                reader = csv.reader(f)
                
                for row in reader:
                    x_train = []
                    for val in row:
                        x_train.append(np.float64(val))
                    X_train.append(np.asanyarray(x_train))

            y_train = []
            with open('./sleepy/processing/algorithms/dtw1nn/TrainingDataLabels.csv', 'r') as f:
                reader = csv.reader(f)
                
                for row in reader:
                    y_train.append(np.int32(row[0]))

            # Initialize model
            model = classifierTSI(X_train, y_train, self.nCluster, self.nLeaf, self.nSeen, 1) 

            model.parent = Tree(None)       

            file_to_load_dill = './sleepy/processing/algorithms/dtw1nn/tree.dill'    
        
            with open(file_to_load_dill, 'rb') as f:
                dictionary = dill.load(f)
                    
            parent = Tree(None)
            sfd(parent, dictionary)
            
            model.parent = parent
    
            model.parent.thisIsLeaf = False
            model.parent.thisIsRoot = True

            inds = np.linspace(0, len(intervals) - 1, len(intervals), dtype = int)
            init_labels = np.zeros((len(intervals)), dtype=int)

            self.model = model
        

        if len(intervals) >= 1:
            signals = [signal.data[interval[0]:interval[1]] for interval in intervals]
            error, prediction, actual, index = model.performance(parent, signals[0:5], init_labels[0:5], windowSize, inds[0:5])

            q = multiprocessing.Queue()
            concurrency = multiprocessing.cpu_count()
            sema = Semaphore(concurrency)
            sim_list = []
            interval = 9
            ind = 0
            if len(intervals) % interval == 0:
                final = int(len(intervals)/interval)
            else:
                final = int(len(intervals)/interval) + 1

            for i in range(final):        
                try:
                    sim_list.append(simulation(model, parent, signals[ind:ind+interval], init_labels[ind:ind+interval], windowSize, inds[ind:ind+interval], sema, q))
                except:
                    sim_list.append(simulation(model, parent, signals[ind:], init_labels[ind:], windowSize, inds[ind:], sema, q))
                ind += interval

            concurrency = multiprocessing.cpu_count()

            error, prediction, actual, index = [], [], [], []
            all_processes = []
            ind1 = 0
            ind2 = concurrency 
            chunks = int(len(sim_list) / concurrency) + 1
            for chunk in range(chunks):
                chunk_processes = []
                try:
                    chunk_sim_list = sim_list[ind1:ind2]
                    ind1 = ind2
                    ind2 = ind2 + concurrency
                except:
                    chunk_sim_list = sim_list[ind1:]

                for sim in chunk_sim_list:
                    sema.acquire()
                    chunk_processes.append(sim)
                    sim.start()        

                for p in chunk_processes:
                    p.join()
                    res = q.get()
                    error.append(res[0])
                    prediction.append(res[1])
                    actual.append(res[2])
                    index.append(res[3])
                    p.close()

                all_processes.append(chunk_processes)

            prediction = list(flatten(prediction))
            actual = list(flatten(actual))
            index = list(flatten(index))

            return np.array([interval for interval,label in zip(intervals,[prediction[i] for i in index]) if label==1])
        else:
            return np.array([])
