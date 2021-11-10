

from sleepy.gui.builder import Builder
from PyQt5.QtWidgets import QWidget
from sleepy.processing.parameter import ParameterBase
import pdb

class Processor:

    def render(self):

        self.buildTree = ParameterBase.getBuildTree(self)

        Builder.setAttributesFromJSON(self.buildTree, self, level = 1)

        return self

    @property
    def options(self):

        try:
            return self.widget
        except AttributeError:

            self.widget = QWidget()

            layout = Builder.build(self.buildTree, self, level = 1)

            self.widget.setLayout(layout)

            return self.widget

class Algorithm(Processor):

    def extract(self, data):
        return

    def filter(self, events, data):
        return events

class Filter(Processor):
    pass
