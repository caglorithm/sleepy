import multiprocessing

class simulation(multiprocessing.Process):
    def __init__(self, obj, parent, xtest, ytest, windowSize, length, sema, q):

        # must call this before anything else
        multiprocessing.Process.__init__(self, args=(1, q))

        # then any other initialization
        self.obj = obj
        self.parent = parent
        self.xtest = xtest
        self.ytest = ytest
        self.windowSize = windowSize
        self.length = length
        self.sema = sema
        self.error = None
        self.prediction = None
        self.actual = None
        self.index = None
        self.q = q

    def run(self):
        self.error, self.prediction, self.actual, self.index = self.obj.performance(self.parent, self.xtest, self.ytest, self.windowSize, self.length)
        self.q.put([self.error, self.prediction, self.actual, self.index])
        self.sema.release()
        return self
