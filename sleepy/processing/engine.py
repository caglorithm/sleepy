
import numpy as np
from functools import partial
from sleepy.processing.signal import Signal
from sleepy.gui.tagging.model.event import EventTypeNotSupported, PointEvent, IntervalEvent
from sleepy.test.debug import tracing

class Engine:

    def run(algorithm, filter, dataset, settings = None):
        """Executes an algorithm and a filter on a dataset. The execution follows
        a pipeline concept. The algorithm first gets called with the entire data
        and produces a set of parameters. Then every epoch in every channel is
        processed by the algorithm isolatedly and is additionally supplied the
        parameters pre-processed. Afterwards the result of each call is
        aggregated and filtered by a post-processing step.

        :param algorithm: Algorithm object that implements a subset of the
        methods extract, compute and filter. Extracts receives the entire data
        and returns a set of parameters. These parameters are plugged into
        compute which is called for each signal in every epoch and every channel.
        The results are aggregated and filtered in the filter method.

        :param filter: Filter object. Must support a call via the
        filter-method.

        :param dataset: Data-set object that provides the properties data,
        samplingRate and epochs.

        :param settings: Optional parameter that is passed to all created events.

        :returns: A list of navigators, one for each channel.
        """

        if filter:
            Engine.__applyPreFilter(filter, dataset)

        labels = dataset.labels

        if algorithm:
            computing = Engine.__getComputeMethod(algorithm, dataset.filteredData)

            labels = Engine.__computeStep(computing, dataset)

        events = Engine.__getEvents(dataset, labels, settings)

        if algorithm:
            events = Engine.__filterStep(algorithm, events, dataset)

        Engine.__setLabelsFromEvents(dataset, events)

        Engine.__setTagsFromDataset(events, dataset)

        return events

    def __format(labels):
        """Formats labels from channel by epoch by label to channel by concatenated
        epoch labels.
        """

        result = []

        for x in labels:

            line = []

            for a in x:

                for e in a:
                    line.append(e)

            result.append(np.array(line))

        return np.array(result)

    def __applyPreFilter(filter, dataset):
        """Applies a given filter to a given dataset and hands the result to
        the dataset in the appropriate format (channel by epoch).
        """

        epochs = range(len(dataset.data))

        filteredData = Engine.__preFilter(filter, dataset, epochs)

        dataset.filteredData = filteredData

    def __preFilter(filter, dataset, epochs):
        """Filters the entire dataset for the extract step.
        """

        numberOfEpochs = len(epochs)

        filteredData = [
            np.array([
                filter.filter(dataset.data[epoch][channel], dataset.samplingRate)
                    for channel in range(len(dataset.data[epoch]))
            ])
                for epoch in epochs
        ]

        return np.array(filteredData)

    def __getComputeMethod(algorithm, data):
        """Executes the extract step and attaches the parameters to the compute
        method of the algorithm.
        """

        extractParameters = algorithm.extract(data)

        if extractParameters is not None:

            if isinstance(extractParameters, tuple):

                return partial(algorithm.compute, *extractParameters)

            else:

                return partial(algorithm.compute, extractParameters)

        else:

            return algorithm.compute

    def __computeStep(computing, dataset):
        """Performs the compute step for each signal in the filtered dataset.
        Converts the resulting, aggregated labels into event instances and
        returns these.
        """

        compute = partial(Engine.__compute, computing, dataset.samplingRate)

        epochs = range(len(dataset.filteredData))

        labels = [
            [
                compute(dataset.filteredData[epoch][channel], dataset.epochs[epoch][0])
                    for channel in range(len(dataset.filteredData[epoch]))
            ]
            for epoch in epochs
        ]

        return Engine.__format(
            Engine.__transposeFirstTwoDimensions(np.array(labels))
        )

    def __compute(computing, samplingRate, data, epochStart):
        """Computes the result of a signal applied to a given algorithm.
        """

        signal = Signal(data, samplingRate)

        labels = computing(signal)

        return ( labels + epochStart ).astype(np.int32).tolist()

    def __filterStep(algorithm, events, dataset):
        """Performs the filter step. The algorithm is supplied with the events
        and the filtered data. The result is used to filter the events.
        The events are first concatenated into one array. The result reduces the
        events array which consists of one array per channel.
        """

        allEvents = np.concatenate(events)

        filteredEvents = algorithm.filter(allEvents, dataset.filteredData)

        Engine.__handleRemovedEvents(allEvents, filteredEvents)

        return [
            [
                event for event in channelEvents if event in filteredEvents
            ]
            for channelEvents in events
        ]

    def __setLabelsFromEvents(dataset, events):
        """Extracts the labels from an array of events and sets the resulting
        array as the new labels of the dataset.
        """

        labels = [
            np.array([
                event.label for event in channelEvents
            ])
            for channelEvents in events
        ]

        dataset.labels = np.array(labels)

    def __setTagsFromDataset(events, dataset):
        """Sets the tags of the dataset to the corresponding events
        """

        for channel in range(len(dataset.tags)):

            for label in range(len(dataset.tags[channel])):

                if dataset.tags[channel][label] == 1:

                    events[channel][label].switchTag()

    def __handleRemovedEvents(allEvents, filteredEvents):
        """Calculates the diff of the input arrays and calls the onRemove method
        for each event that has been removed by the algorithm.
        """

        removedEvents = [ event for event in allEvents if event not in filteredEvents]

        for event in removedEvents:

            event.onRemove()

    def __transposeFirstTwoDimensions(array):
        """Transposes the first two dimensions of a given array
        """

        lengthOfShape = len(array.shape)

        flippedShape = list(range(lengthOfShape))

        flippedShape[0] = 1
        flippedShape[1] = 0

        return array.transpose(tuple(flippedShape))

    def __getEvents(dataset, labels, settings):
        """Creates events from a fully computed dataset (labels, tags, filteredData).
        Labels are stored in the dataset channel-wise. Calls a creator function
        for each label, appending the settings object.
        """

        createEvents = partial(Engine.__createEvent, settings)

        return np.array(dataset.forEachChannel(labels, createEvents))

    def __createEvent(settings, label, dataSource):
        """Creates an event from a given label, and a given data source.
        """

        if Engine.__isPoint(label):

            event = PointEvent(*label, dataSource, settings)

        elif Engine.__isInterval(label):

            event = IntervalEvent(*label, dataSource, settings)

        else:
            raise EventTypeNotSupported

        return event

    def __isPoint(label):
        """Checks whether the label satisfies all criterias to be used as
        a PointEvent.
        """

        return label.shape == (1,)

    def __isInterval(label):
        """Checks whether the label satisfies all criterias to be used as
        a IntervalEvent.
        """

        return label.shape == (2,)
