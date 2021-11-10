
from sleepy.gui.exceptions import UserCancel

def visualize(function):
    """Decorator function for methods that should only apply changes if the
    control is active and whose actions neccesitate a rerender of the ui.
    """

    def visualizing(self, *args):

        if self.active:

            function(self, *args)

            self.visualizeTag()

    return visualizing

class MultiChannelControl:
    """Extension for :class:`TaggingControl` supporting additional functionality
    for handling multiple channels.
    """

    def getChannelCounterString(self):
        """Creates a string containing the current channel + 1 and the
        number of channels.
        """

        counterString = ''

        if self.settings.showIndex:

            outOf = len(self.navigators)

            counterString = '{}/{}'.format(self.channel + 1, outOf)

        return counterString

    def installNavigator(self, navigator):
        """Installs a navigator to the control and checks whether the navigator
        is valid. The exception will not be catched.
        """

        self.validate(navigator)

        self.navigator = navigator

    @property
    def channel(self):
        """Returns the index of the current channel if a navigator is currently
        set. Returns -1 otherwise.
        """

        if self.navigator:

            return self.navigators.index(self.navigator)

        else:

            return -1

    def getNextChannel(self, index):
        """Selects the next channel in a channel ring.
        """

        return ( index + 1 ) % len(self.navigators)

    def getPreviousChannel(self, index):
        """Selects the previous channel in a channel ring.
        """

        return ( index - 1 ) % len(self.navigators)

    @visualize
    def nextChannel(self, startingFrom = None):
        """Select the next channel and install the corresponding navigator.
        Tries to confirm the next channel until a suitable is found. Before
        trying to installing the same navigator twice, cancel.
        """

        channel = (startingFrom - 1) if startingFrom is not None else self.channel

        initialIndex = -1

        index = self.getNextChannel(channel)

        # Full round
        while index != initialIndex:

            if initialIndex < 0:
                initialIndex = index

            try:
                self.installNavigator(
                    self.navigators[index]
                )

                self.configureTimeline()

                return
            except:

                index = self.getNextChannel(index)

        self.view.tellUserNavigationFlawed()

        raise UserCancel

    @visualize
    def previousChannel(self):
        """Select the previous channel and install the corresponding navigator
        """

        initialIndex = -1

        index = self.getPreviousChannel(self.channel)

        # Full round
        while index != initialIndex:

            if initialIndex < 0:
                initialIndex = index

            try:
                self.installNavigator(
                    self.navigators[index]
                )

                self.configureTimeline()

                return
            except:

                index = self.getPreviousChannel(index)

        self.view.tellUserNavigationFlawed()

        raise UserCancel
