
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class RandomForest(Algorithm):

    def __init__(self):

        self.name = "RandomForest"
        
    def calc_fs(self,X):
        features=np.zeros((X.shape[0],17),dtype='float32')
        # Features 0-4: Length, Minimum, Maximum, Amplitude, Ratio of Min to max
        features[:,0]=sum((X.T!=0))
        features[:,1]=np.min(X,axis=1)
        features[:,2]=np.max(X,axis=1)
        features[:,3]=np.max(X,axis=1)-np.min(X,axis=1)
        a=np.max(X,axis=1)
        b=np.abs(np.min(X,axis=1))
        features[:,4]=np.divide(a,b, out=np.zeros_like(a), where=b!=0)
    
        #Features 5-8: Length until middle zero crossing, rest length, amount of local extremas, amount of turning points
        dif=np.diff(X>0)
        diffs=np.nonzero(dif)
        length=np.zeros_like(dif, dtype=int)
        length[dif==True]=diffs[1]
        length=-np.sort(-length)
        length[:,:2]
    
        features[:,5]=length[:,1]
        features[:,6]=length[:,0]-length[:,1]
        features[:,7]=np.sum(np.diff((np.diff(X)>0)),axis=1)
        features[:,8]=np.sum(np.diff(np.diff(np.diff(X))>0),axis=1)
    
        #Feature 9-11: Maximal 3 frequencies
        ps = np.abs(np.fft.fft(X))**2
        freqs=np.fft.fftfreq(X.shape[1], 1/10)
        features[:,9:12]=np.abs(freqs[np.argsort(ps,axis=1)[:,:3]])
    
        #Feature 12-14: Max and min of Wavelet Decomposition Single Level Detail coefficients and ratio of each other
        import pywt
        (cA, cD) = pywt.dwt(X, 'db1')
        features[:,12]=np.max(cD,axis=1)
        features[:,13]=np.min(cD,axis=1)
        features[:,14]=np.max(cD,axis=1)/np.min(cD,axis=1)
    
        #Feature 15-16: Time and frequency of maximum STFT 
        from scipy import signal
        f, t, Zxx = signal.stft(X, 100, nperseg=20)
        max_idx = Zxx.reshape(Zxx.shape[0],-1).argmax(1)
        maxpos_vect = np.column_stack(np.unravel_index(max_idx, Zxx[0,:,:].shape))
        features[:,15]=t[maxpos_vect[:,1]]
        features[:,16]=f[maxpos_vect[:,0]]
        return features
        

    def compute(self, signal):
        
        if not hasattr(self, 'RF_model'):
            # generate model
            import joblib
            model= joblib.load("./sleepy/processing/algorithms/RandomForest/randomforest.sav")
    
            self.RF_model=model

        intervals = signal.findWaves()
        if len(intervals)>=1:
            signals = [signal.data[interval[0]:interval[1]] for interval in intervals]
            from keras.preprocessing.sequence import pad_sequences
            # downsampling and padding
            resamplingRate=signal.samplingRate/50
            signals=[np.interp(np.arange(0, len(sig), resamplingRate), np.arange(0, len(sig)), sig) for sig in signals]
            signals=pad_sequences(signals, padding='post',dtype='float64',maxlen=126)
            
            signals=self.calc_fs(signals)
            labels=self.RF_model.predict(signals)

            return np.array([interval for interval,label in zip(intervals,labels) if label==1])
        else:
            return np.array([])
