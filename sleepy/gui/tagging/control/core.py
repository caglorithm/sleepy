
from sleepy.gui.exceptions import UserCancel, NoNavigatorError, NavigatorEmptyError
from sleepy.gui.tagging.control.channels import MultiChannelControl, visualize
from PyQt5.QtWidgets import QMessageBox
import pdb

class TaggingControl(MultiChannelControl):

    def __init__(self, parent, settings):

        self.parent = parent
        self.settings = settings
        self.active = False

    @property
    def navigator(self):
        try:
            return self._navigator
        except AttributeError:
            return None

    @navigator.setter
    def navigator(self, navigator):
        """Sets the navigator internally and registers event handlers for a set
        of data events of the navigator. On initialize, the corresponding event
        handlers get called with the initial value of the event and on future
        events, whereas connect only fires upon future events.
        """

        self._navigator = navigator

        self._navigator.onChangesMade.initialize(
            [self.onChangesMade]
        )

        self._navigator.onPosition.initialize(
            [self.onPosition]
        )

        self._navigator.onPosition.connect(
            [self.updateTimeline]
        )

    @navigator.deleter
    def navigator(self):
        del self._navigator

    def close(self):
        """If any navigators are currently installed, the user must be asked
        to confirm the change. After closing the navigators and the buffered
        dataset have to be removed.

        :raises UserCancel: Raised if user aborts the closing process.
        """

        try:

            self.navigators

            self.notifyUserOfSwitch()

        except AttributeError:
            pass

        self.onClose()

        self.active = False

    def onClose(self):
        """Removes navigators and dataset from the control and tells the view
        to remove the toolbar.
        """

        try:
            del self.navigators
        except AttributeError:
            pass

        try:
            del self.navigator
        except AttributeError:
            pass

        try:
            del self.dataset
        except AttributeError:
            pass

        #import gc; gc.collect()
        if self.active:
            self.view.removeToolBar()

    @visualize
    def onNextClick(self, *args):
        """Gets registered by the view and is called if the user navigates
        forward. Propagates this action to the navigator and ensures that
        the changes will be reflected by the view.
        """

        self.navigator.selectNext()

    @visualize
    def onPreviousClick(self, *args):
        """Gets registered by the view and is called if the user navigates
        backward. Propagates this action to the navigator and ensures that
        the changes will be reflected by the view.
        """

        self.navigator.selectPrevious()

    @visualize
    def onTaggingClick(self, *args):
        """Gets registered by the view and is called if the user tags an event.
        Propagates this action to the navigator and ensures that
        the changes will be reflected by the view.
        """

        self.navigator.switchSelectionTag()

    @visualize
    def visualizeOnOpen(self, *args):
        """Called when loading new data, before presentation. Updates the
        window title and propagates the open event to the view.
        """

        self.updateWindowTitle()

        self.view.open()

    def onPosition(self, position):
        """Event handler for the :class:`DataEvent` onPosition of the navigator.
        Gives the navigator access to letting its current event plot its
        data on the canvas provided by the view.
        """

        self.view.plot(self.navigator.plot)

        self.updateWindowTitle()

    def redraw(self):
        """Forces update on current position and updates the window title.
        This method is used when e.g. user events are added, to refresh the
        current plot even if the position of the current event has not changed.
        """

        self.onPosition(self.navigator.position)

        self.updateWindowTitle()

    def updateTimeline(self, *args):
        """Updates the timeline on a change of position. This does not require
        every point of the dataset to be redrawn. For that task compare method
        configureTimeline.
        """

        _, currentPoint, currentLimits = self.navigator.getTimelineData()

        self.timeline.update(currentPoint, currentLimits)

        self.view.draw()

    @visualize
    def onTimelineClick(self, time):
        """Handles a double-click on the timeline by telling the navigator
        to select the event that is closest to the timestamp that the user
        double-clicked.
        """

        self.navigator.selectClosestToTime(time)

    def onMainDblClick(self, event):
        """Called if the main figure in the view is double-clicked. This method
        tries to identify the given event as a user event. If this can be done,
        then the user is offered to remove the event. Otherwise, the user is
        offered to create a new user event here. The API-method of the view
        that are called build a context menu and move it to the current cursor
        position. The context menu for event creation is only displayed if the
        user actually clicked on the graph. The navigator offers a method to
        check that.
        """

        userEvent = self.navigator.findUserEvent(event)

        if not userEvent:

            if self.navigator.onGraphClick(event):

                self.view.showMenuUserEventCreate(event)

        else:

            self.view.showMenuUserEventRemove(userEvent)

    def createUserEvent(self, event):
        """Propagates to the navigator to add an event and then forces a redraw.
        """

        self.navigator.addUserEvent(event)

        self.redraw()

        self.configureTimeline()

    def removeUserEvent(self, userEvent):
        """Propagates to the navigator to add a user event and then forces a
        redraw.
        """

        self.navigator.removeUserEvent(userEvent)

        self.redraw()

        self.configureTimeline()

    def open(self, preprocessing):
        """Loads a navigator and a dataset from a preprocessing instance.
        Before accepting the new data, this method validates whether the
        navigator contains displayable data and tells the user that the
        navigation is flawed otherwise.
        If the navigator is valid, this method buffers navigator and dataset,
        configures the timeline with data from the navigator, restores potential
        checkpoints and fires an initial visualization of the view.

        :param preprocessing: Instance of :class:`Preprocessing` that can be run
        to retrieve a set of navigators and a dataset.

        :raises UserCancel: Raised if either the user cancels the preprocessing
        or there are no empty navigators.
        """

        try:
            navigators, dataset = preprocessing.run()
        except UserCancel:
            raise

        if len(navigators) > 0:

            self.navigators = navigators
        else:

            self.view.tellUserNavigationFlawed()

            raise UserCancel

        self.dataset = dataset

        if self.navigator:
            del self.navigator

        self.active = True

        self.onAfterActivate()

    def onAfterActivate(self):
        """Do visualization after the control has been set active. This involves
        setting up the timeline, restoring checkpoints and visualizing the setup.
        This method should be called by the environment after it was activated.
        """

        if not self.active:
            return

        self.nextChannel()

        self.configureTimeline()

        self.restoreCheckPoint()

        self.visualizeOnOpen()

    def configureTimeline(self):
        """Lets the view create a new timeline and plots the timeline points.
        This method can be used to rerender the entire timeline at any given
        point.
        """

        self.view.clearTimelineAxis()

        self.timeline = self.view.getTimeline()

        timelineData = self.navigator.getTimelineData()

        self.timeline.plot(*timelineData)

        self.view.draw_idle()

    def validate(self, navigator):
        """Validates whether a given navigator exists and contains data. Otherwise
        appropriate messages are displayed to the user and the method raises a
        NoNavigatorError exception.
        """

        if navigator is None:
            raise NoNavigatorError

        if navigator.maximumPosition == 0:
            raise NavigatorEmptyError

    @visualize
    def refresh(self):
        """Forces an update on the current position. Can be used to apply any
        updates on settings-values or similar to the screen.
        """

        self.navigator.onPosition.trigger()

    def save(self):
        """Tells the fileLoader to save the current dataset. If this does not
        result in an exception, then the dataset is considered saved, which
        needs reflection in the navigator (e.g. reset changesMade flag).
        """

        if not self.active:
            return

        path = self.view.getSaveFileName()

        self.dataset.save(path, self.navigators)

        self.navigator.onSave()

    def onSaveFile(self):
        """Wraps around the save method but suppresses the UserCancel and
        returns None instead.
        """

        try:
            self.save()
        except UserCancel:
            return

    def onChangesMade(self, changesMade):
        """Event handler for the changesMade event of the navigator. Keeps track
        of whether changes are made, updates the menu options (save disabled if
        no changes made) and updates the window title.
        """

        self.changesMade = changesMade

        self.updateMenuOptions()

        self.updateWindowTitle()

    def updateWindowTitle(self):
        """Creates a window title for the application based on the currently
        selected filename, the name of the app, whether the user has made
        changes on the dataset and the counter of the current events with
        respect to the number of events detected.
        """

        if self.dataset.filename != '':

            windowTitle = '{} - {}'.format(self.parent.control.name, self.dataset.filename)

        else:

            windowTitle = self.parent.control.name

        if self.changesMade:

            windowTitle += '*'

        channelCounterString = self.getChannelCounterString()

        if channelCounterString != '':
            windowTitle += " - Channel: {}".format(channelCounterString)

        counterString = self.getCounterString()

        if counterString != '':
            windowTitle += " - Sample: {}".format(counterString)

        self.parent.window.setWindowTitle(windowTitle)

    def getCounterString(self):
        """Creates a string containing the current position + 1 and the
        number of events managed by the navigator.
        """

        counterString = ''

        if self.settings.showIndex:

            outOf = self.navigator.maximumPosition

            counterString = '{}/{}'.format(self.navigator.position + 1, outOf)

        return counterString

    def updateMenuOptions(self):
        """Disables the save menu action if no changes are made and disables the
        clear menu action if the control is not active.
        """

        disableSaveOption = not self.changesMade
        self.parent.saveFile.setDisabled(disableSaveOption)

        disableClearOption = not self.active
        self.parent.clearFile.setDisabled(disableClearOption)

    def notifyUserOfSwitch(self):
        """Starts the creation of a potential checkpoint and asks the user
        whether it is alright to switch to a different dataset or to the
        null screen.
        """

        self.setCheckpoint()

        changesMade = self.navigator.changesMade

        # We want to enable that if the user cancels the Save-Dialog, it prompts
        # the question again
        while changesMade:

            reply = self.view.askUserForSwitch()

            if reply == QMessageBox.Cancel:
                raise UserCancel

            elif reply == QMessageBox.Save:

                try:

                    self.save()
                except UserCancel:
                    continue
            return

    def restoreCheckPoint(self):
        """Tries to recover the last checkpoint saved in the current dataset.
        """

        if self.settings.useCheckpoints:

            checkpoint = self.dataset.checkpoint

            if checkpoint:

                index, position = checkpoint

                answer = self.view.askUserForCheckPointRestore(position + 1, index + 1)

                if answer == QMessageBox.Yes:

                    self.navigators[index].position = position

                    self.nextChannel(index)

    def setCheckpoint(self):
        """Tries to save the current position as a checkpoint in the dataset.
        """

        if self.settings.useCheckpoints:

            answer = self.view.askUserForCheckPoint()

            if answer == QMessageBox.Yes:

                position = self.navigator.position

                index = self.navigators.index(self.navigator)

                self.dataset.checkpoint = (index, position)

                self.navigator.changesMade = True

            elif answer == QMessageBox.Cancel:

                raise UserCancel


    def visualizeTag(self):
        """Called by the visualize decorator. This methods decides on the
        stylesheet and text of the tagging button and propagtes this change
        to the view.
        """

        if self.navigator.selectionTag:

            self.view.setButtonStyle(
                stylesheet = 'QPushButton { background-color: red; color: white; }',
                text = 'Tagged as False-Positive'
            )

        else:

            self.view.setButtonStyle(
                stylesheet = '',
                text = 'Not Tagged'
            )
