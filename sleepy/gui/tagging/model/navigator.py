
from sleepy.gui.tagging.core import DataEvent
from sleepy.gui.tagging.model.event import UserPointEvent
from sleepy.gui.tagging.model.exceptions import UserEventExists
import numpy as np

class Navigator:
    def __init__(self, events, changesMade = False):

        self.events = events
        self.userEvents = []

        self.maximumPosition = len(events)

        self.stateBeforeChanges = self.getCurrentTags()
        self.eventsBeforeChanges = self.events
        self.changesMadeBeforeCreation = changesMade

        self.onChangesMade = DataEvent(changesMade)
        self.onPosition = DataEvent(0)

    @property
    def position(self):
        return self.onPosition.value

    @position.setter
    def position(self, value):
        self.onPosition.value = value

    @property
    def changesMade(self):
        return self.onChangesMade.value

    @changesMade.setter
    def changesMade(self, value):
        self.onChangesMade.value = value

    @property
    def currentPointInSeconds(self):
        return self.selectedEvent.currentPointInSeconds

    @property
    def currentLimitsInSeconds(self):
        return self.selectedEvent.absoluteLimitsInSeconds

    @property
    def pointsInSeconds(self):
        return list(map(lambda e: e.currentPointInSeconds, self.events))

    @property
    def selectedEvent(self):
        return self.events[self.position]

    @property
    def tagsInSeconds(self):

        selectedEvents = list(filter(lambda e: e.tagged, self.events))

        return list(map(lambda e: e.currentPointInSeconds, selectedEvents))

    @property
    def selectionTag(self):
        return self.selectedEvent.tagged

    def selectNext(self):

        if (self.position + 1) == self.maximumPosition:
            self.position = 0
        else:
            self.position += 1

    def selectPrevious(self):

        if self.position == 0:
            self.position = self.maximumPosition - 1
        else:
            self.position -= 1

    def selectClosestToTime(self, time):

        pointsInSeconds = np.array(self.pointsInSeconds)

        self.position = np.argmin(np.abs(pointsInSeconds - time))

    def reset(self):
        self.position = 0

    def plot(self, axis):
        self.selectedEvent.plot(axis)

    def switchSelectionTag(self):
        """Switch the tag of the currently selected event.
        """

        self.selectedEvent.switchTag()

        self.updateChangesMade()

    def updateChangesMade(self):
        """Implements a sequence of checks to set changesMade to true or false.
        """

        self.changesMade = not np.array_equal(
            self.stateBeforeChanges, self.getCurrentTags()
        ) or self.changesMadeBeforeCreation or not np.array_equal(
            list(map(lambda e:e.currentPointInSeconds, self.eventsBeforeChanges)),
            list(map(lambda e:e.currentPointInSeconds, self.events))
        )


    def onSave(self):

        self.changesMade = False

        self.changesMadeBeforeCreation = False

        self.stateBeforeChanges = self.getCurrentTags()

        self.eventsBeforeChanges = self.events

    def getCurrentTags(self):

        tags = []

        for event in self.events:
            tags.append(event.tagged)

        return np.array(tags)

    def getCurrentLabels(self):

        labels = []

        for event in self.events:
            labels.append(event.label)

        return np.array(labels)

    def getLabelPartition(self):
        """Returns the labels belonging to computed events and the labels
        belonging to user events as two separate numpy arrays.
        """

        computed = list(filter(lambda e: e not in self.userEvents, self.events))

        user = list(filter(lambda e: e in self.userEvents, self.events))

        return self.getLabelsFromEvents(computed), self.getLabelsFromEvents(user)

    def getLabelsFromEvents(self, events):
        """Returns the labels of a given set of events as a numpy array.
        """

        labelsAsList = list(map(lambda e: e.label, events))

        return np.array(labelsAsList)

    def createUserEvent(self, pointInSamples):

        currentUserPoints = list(map(lambda e: e.point, self.userEvents))

        if pointInSamples not in currentUserPoints:

            # User-events are always point-events
            return UserPointEvent(
                pointInSamples,
                self.selectedEvent.dataSource,
                self.selectedEvent.applicationSettings
            )
        else:
            raise UserEventExists

    def addUserEvent(self, event):
        """Called by pyplot when a user event has to be added.
        """

        pointInSamples = self.selectedEvent.convertSeconds(event.xdata)

        self.addUserEventSamples(pointInSamples)

    def addUserEventSamples(self, pointInSamples):
        """Add a user event in samples unit. Can be used as an API but is also
        internally used when receiving an event from pyplot.
        """

        try:
            userEvent = self.createUserEvent(pointInSamples)
        except UserEventExists:
            return

        self.addCreatedUserEvent(userEvent)

    def addCreatedUserEvent(self, userEvent):
        """Adds an userEvent instance and ensures consistency in the events list.
        """

        selectedEvent = self.selectedEvent

        self.events.append(userEvent)
        self.userEvents.append(userEvent)

        self.ensureConsistency()

        # Make sure that position is updated if inserted before current
        # event
        if selectedEvent.point > userEvent.point:
            self.position += 1

        self.updateChangesMade()

    def removeUserEvent(self, userEvent):

        selectedEvent = self.selectedEvent

        self.events.remove(userEvent)
        self.userEvents.remove(userEvent)

        userEvent.onRemove()

        self.ensureConsistency()

        # Make sure that position is updated if inserted before current
        # event
        if selectedEvent.point > userEvent.point:
            self.position -= 1

        self.updateChangesMade()

    def findUserEvent(self, event):

        for userEvent in self.userEvents:

            if userEvent.artist:

                if userEvent.artist.contains(event)[0]:

                    return userEvent

    def onGraphClick(self, event):

        return self.selectedEvent.onGraphClick(event)

    def ensureConsistency(self):

        oldEvents = self.events

        self.events = sorted(
            self.events, key = lambda event: event.point
        )

        self.maximumPosition = len(self.events)

        if oldEvents != self.events:
            self.changesMade = True

    def getTimelineData(self):
        """Returns a set of all points, the currently selected point and the
        currently selected interval, which specifies the data for a timeline,
        as a tuple.
        """

        return (
            self.pointsInSeconds,
            self.currentPointInSeconds,
            self.currentLimitsInSeconds
        )

    def getComputedEventTags(self):
        """Returns the tags that belong to events that are not user events.
        """

        tags = [ e.tagged for e in self.events if e not in self.userEvents ]

        return np.array(tags)
