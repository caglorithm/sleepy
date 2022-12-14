
from sleepy.processing.processor import Algorithm
from sleepy.processing.parameter import Parameter
import numpy as np

class BiLSTM(Algorithm):

    def __init__(self):

        self.name = "BiLSTM"
        

    def compute(self, signal):
        
        if not hasattr(self, 'BiLSTM_model'):
            # generate model
            from keras.models import Sequential
            from keras.layers import InputLayer, Bidirectional, LSTM, Dense, TimeDistributed, Flatten, Dropout, LeakyReLU
            from tensorflow.keras.optimizers import Adam
    
            model = Sequential()
            model.add(InputLayer(input_shape=(126, 1)))
            #BiLSTM
            model.add(Bidirectional(LSTM(256, return_sequences=True)))
            #Dense1
            model.add(TimeDistributed(Flatten()))
            model.add(Dropout(0.8))
            model.add(TimeDistributed(Dense(50, activation=LeakyReLU())))
            #Dense2
            model.add(Flatten())
            model.add(Dropout(0.8))
            model.add(Dense(30, activation=LeakyReLU()))
            # Output
            model.add(Dense(1, activation='sigmoid'))
            #compile
            model.compile(loss='binary_crossentropy',optimizer=Adam(lr=0.0005) , metrics='accuracy')
            model.load_weights("./sleepy/processing/algorithms/BiLSTM/model_weights.h5")
    
            self.BiLSTM_model=model

        intervals = signal.findWaves()
        if len(intervals)>=1:
            signals = [signal.data[interval[0]:interval[1]] for interval in intervals]
            from keras.preprocessing.sequence import pad_sequences
            # downsampling and padding
            resamplingRate=signal.samplingRate/50
            signals=[np.interp(np.arange(0, len(sig), resamplingRate), np.arange(0, len(sig)), sig) for sig in signals]
            signals=pad_sequences(signals, padding='post',dtype='float64',maxlen=126)
            signals=signals.reshape((signals.shape[0], 126, 1))
            labels=self.BiLSTM_model.predict(signals)>0.5
            if len(labels)>1:
                labels=np.squeeze(labels)

            return np.array([interval for interval,label in zip(intervals,labels) if label])
        else:
            return np.array([])
