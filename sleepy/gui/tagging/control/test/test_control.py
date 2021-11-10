

import unittest
from unittest.mock import MagicMock
from sleepy.gui.tagging.control import TaggingControl
from sleepy.gui.exceptions import UserCancel
from PyQt5.QtWidgets import QMessageBox
from sleepy.test.core import TestBase

class ControlTest(unittest.TestCase):

    def standardScenario():

        view, app, settings = TestBase.getBasics(active = True, name = 'TestApplication')

        control = TaggingControl(app, settings)

        control.view = view

        events = TestBase.getEvents([1,2,3], settings, TestBase.getDataSource())

        navigator = TestBase.getNavigator(events, changesMade = False)

        dataset = TestBase.getDataset("test/path/TestFile")

        processing = TestBase.getPreprocessing(dataset = dataset, navigators = [navigator])

        return view, app, settings, control, navigator, processing

    def multipleNavigatorScenario():

        view, app, settings = TestBase.getBasics(active = True, name = 'TestApplication')

        control = TaggingControl(app, settings)

        control.view = view

        events1 = TestBase.getEvents([1,2,3], settings, TestBase.getDataSource())
        events2 = TestBase.getEvents([3,4,5], settings, TestBase.getDataSource())

        navigator1 = TestBase.getNavigator(events1, changesMade = False)

        navigator2 = TestBase.getNavigator(events2, changesMade = False)

        dataset = TestBase.getDataset("test/path/TestFile")

        processing = TestBase.getPreprocessing(dataset = dataset, navigators = [navigator1, navigator2])

        return view, app, settings, control, [navigator1, navigator2], processing


    def test_open_no_navigator(self):
        """Opening the processing should cause a UserCancel exception.
        """

        view, app, settings = TestBase.getBasics(active = False, name = 'TestApplication')

        control = TaggingControl(app, settings)
        control.view = view

        processing = TestBase.getPreprocessing(navigators = [])

        try:
            control.open(processing)

        except UserCancel:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test_open_empty_navigator(self):
        """Opening the processing should be possible but when the control tries to
        find a navigator in the onAfterActivate method, there should be a UserCancel.
        """

        view, app, settings = TestBase.getBasics(active = False, name = 'TestApplication')

        control = TaggingControl(app, settings)
        control.view = view

        events = TestBase.getEvents([], settings)

        processing = TestBase.getPreprocessing(navigators = [TestBase.getNavigator(events)])

        view.active = True

        try:
            control.open(processing)
        except UserCancel:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test_open_valid_navigator_windowtitle_and_button_red(self):
        """Window title must contain an asterisk.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        navigator.switchSelectionTag()

        control.open(processing)

        app.window.setWindowTitle.assert_called_with('TestApplication - TestFile*')

    def test_open_valid_navigator_windowtitle_showIndex_no_asterisk(self):
        """Window title must not contain an asterisk but channel and sample
        counter information.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        settings.showIndex = True

        control.open(processing)

        app.window.setWindowTitle.assert_called_with('TestApplication - TestFile - Channel: 1/1 - Sample: 1/3')

    def test_open_valid_navigator_windowtitle_showIndex(self):
        """Window title must contain an asterisk as well as channel and sample
        counter information.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        settings.showIndex = True

        navigator.switchSelectionTag()

        control.open(processing)



        app.window.setWindowTitle.assert_called_with('TestApplication - TestFile* - Channel: 1/1 - Sample: 1/3')

    def test_open_valid_navigator_visualizeTag_active_tagged(self):
        """Tagging button must be red on selection-tag switch.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        navigator.switchSelectionTag()

        control.open(processing)


        view.setButtonStyle.assert_called_with(
            stylesheet = 'QPushButton { background-color: red; color: white; }',
            text = 'Tagged as False-Positive'
        )

    def test_open_valid_navigator_visualizeTag_active_not_tagged(self):
        """Button must be set gray if not tagged.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)


        view.setButtonStyle.assert_called_with(
            stylesheet = '',
            text = 'Not Tagged'
        )

    def test_open_valid_navigator_with_checkpoints_user_yes(self):
        """Position of navigator should be set to the checkpoint that the
        user approved of.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        settings.useCheckpoints = True

        view.askUserForCheckPointRestore = MagicMock(return_value = QMessageBox.Yes)

        checkpoint = 2
        _, dataset = processing.run()
        dataset.checkpoint = (0, checkpoint)

        control.open(processing)

        self.assertEqual(
            navigator.position,
            checkpoint
        )

    def test_open_valid_navigator_with_checkpoints_user_yes_different_channel(self):
        """Position of navigator should be set to the checkpoint that the
        user approved of and the correct navigator should be selected.
        """

        view, app, settings, control, navigators, processing = ControlTest.multipleNavigatorScenario()

        settings.useCheckpoints = True

        view.askUserForCheckPointRestore = MagicMock(return_value = QMessageBox.Yes)

        checkpoint = 2
        _, dataset = processing.run()
        dataset.checkpoint = (1, checkpoint)

        control.open(processing)

        self.assertEqual(control.navigator, navigators[1])

        self.assertEqual(
            navigators[1].position,
            checkpoint
        )

    def test_open_valid_navigator_with_checkpoints_user_no(self):
        """Position of navigator should not be set to the checkpoint that the
        user did not approve of.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        settings.useCheckpoints = True

        view.askUserForCheckPointRestore = MagicMock(return_value = QMessageBox.No)

        checkpoint = 2
        _, dataset = processing.run()
        dataset.checkpoint = (0, checkpoint)

        control.open(processing)

        self.assertEqual(
            navigator.position,
            0
        )

    def test_open_timeline_intial_call(self):
        """Timeline mock is called with proper arguments given a set of points
        in a navigator.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)


        dataSource = navigator.events[0].dataSource

        # Timeline is a mock supplied from the view
        control.timeline.plot.assert_called_with(
            [1/dataSource.samplingRate, 2/dataSource.samplingRate, 3/dataSource.samplingRate],
            1/dataSource.samplingRate,
            (0.0, 1.1)
        )

    def test_navigate_timeline_supplied(self):
        """Timeline mock is called with proper arguments given a set of points
        in a navigator on a position update.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)


        control.onNextClick()

        dataSource = navigator.events[0].dataSource

        control.timeline.update.assert_called_with(
            2/dataSource.samplingRate,
            (0.0, 1.2)
        )

    def test_onTimelineClick_tag_visualized(self):
        """Clicking on the timeline supplies the navigator with the correct time
        and visualizes potential changes on the tag.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)

        navigator.selectClosestToTime = MagicMock()
        control.visualizeTag = MagicMock()

        control.onTimelineClick(1.3)

        navigator.selectClosestToTime.assert_called_with(1.3)

        control.visualizeTag.assert_called()

    def test_navigate_forward_active(self):
        """Navigating forward two times increases the position of navigator about
        two.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)

        self.assertEqual(navigator.position, 0)

        control.onNextClick()
        control.onNextClick()

        self.assertEqual(navigator.position, 2)

    def test_navigate_backward_active(self):
        """Navigating forward two times decreases the position of navigator about
        two.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)

        self.assertEqual(
            navigator.position,
            0
        )

        control.onPreviousClick()
        control.onPreviousClick()

        self.assertEqual(
            navigator.position,
            1
        )

    def test_onTaggingClick_active_set(self):
        """Clicking on tagging should set the tag of the selected event.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)

        self.assertEqual(navigator.selectionTag, 0)

        control.onTaggingClick()

        self.assertEqual(navigator.selectionTag, 1)

    def test_onTaggingClick_active_reset(self):
        """Clicking twice on tagging should set and then reset the tag of the selected event.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()

        control.open(processing)

        self.assertEqual(navigator.selectionTag, 0)

        control.onTaggingClick()
        control.onTaggingClick()

        self.assertEqual(navigator.selectionTag, 0)

    def test_notifyUserOfSwitch_no_changes(self):
        """Without changes made the user should not be asked for saving and
        the save method should not be called.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForSwitch = MagicMock()
        control.save = MagicMock()

        control.open(processing)

        control.notifyUserOfSwitch()

        view.askUserForSwitch.assert_not_called()
        control.save.assert_not_called()

    def test_notifyUserOfSwitch_changes_cancel(self):
        """Changes were made but checkpoints are disabled in the settings.
        The user cancels the saving process.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForSwitch = MagicMock(return_value = QMessageBox.Cancel)
        control.save = MagicMock()

        control.open(processing)

        navigator.switchSelectionTag()

        try:
            control.notifyUserOfSwitch()

            self.assertTrue(False)
        except UserCancel:
            pass

        view.askUserForSwitch.assert_called()
        control.save.assert_not_called()

    def test_notifyUserOfSwitch_changes_discard(self):
        """Changes were made but checkpoints are disabled in the settings.
        The user discards the saving process. No UserCancel but also no saving
        methods are called
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForSwitch = MagicMock(return_value = QMessageBox.Discard)
        control.save = MagicMock()

        control.open(processing)


        navigator.switchSelectionTag()

        control.notifyUserOfSwitch()

        view.askUserForSwitch.assert_called()
        control.save.assert_not_called()

        self.assertEqual(navigator.changesMade, True)

    def test_notifyUserOfSwitch_changes_save(self):
        """Changes were made but checkpoints are disabled in the settings.
        The user accepts the saving process.
        1. the processing was called to save the data.
        2. the navigator's onSave method has been called, i.e. changes made are
           reset.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForSwitch = MagicMock(return_value = QMessageBox.Save)

        control.open(processing)

        navigator.switchSelectionTag()

        control.notifyUserOfSwitch()

        view.askUserForSwitch.assert_called()
        _, dataset = processing.run()
        dataset.save.assert_called()

        self.assertEqual(navigator.changesMade, False)

    def test_notifyUserOfSwitch_checkpoints_user_no(self):
        """No changes but checkpoints are activated. User answers no.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForCheckPoint = MagicMock(return_value = QMessageBox.No)
        settings.useCheckpoints = True

        _, dataset = processing.run()

        control.open(processing)

        control.notifyUserOfSwitch()

        view.askUserForCheckPoint.assert_called()
        self.assertEqual(dataset.checkpoint, None)

    def test_notifyUserOfSwitch_checkpoints_user_yes(self):
        """No changes but checkpoints are activated. User answers yes.
        Checkpoint must be set in dataset.
        """

        view, app, settings, control, navigator, processing = ControlTest.standardScenario()
        view.askUserForCheckPoint = MagicMock(return_value = QMessageBox.Yes)
        settings.useCheckpoints = True

        _, dataset = processing.run()

        control.open(processing)

        control.onNextClick()

        control.notifyUserOfSwitch()

        view.askUserForCheckPoint.assert_called()

        self.assertEqual(dataset.checkpoint, (0,1))
