
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QCheckBox, QTabWidget, QWidget
from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox
from sleepy.gui.builder.customwidgets import CustomQSpinBox, CustomQCheckBox, CustomQDoubleSpinBox, Custom0To1DoubleSpinBox, CustomQColorPicker
from functools import partial
from pydoc import locate
import json
import pdb
import inspect
import codecs

class Builder:

    def build(tree, control, level = 2):
        """API-call for building a QVBoxLayout from a given tree.
        The tree can be a path to a json file or a dictionary. The control has
        to implement the getCallback method that provides a callable for a given
        key. Level 2 returns layout containing QGroupBoxes, containing QWidgets,
        Level 3 returns layout conaining QTabWidgets, containing QGroupBoxes,
        containing QWidgets.
        """

        tree = Builder.getDict(tree)

        if level == 1:

            return Builder.constructBoxLayout(tree, control)

        if level == 2:

            return Builder.buildBoxes(tree, control)

        elif level == 3:

            return Builder.buildTabs(tree, control)

    def setAttributesFromJSON(tree, control, level = 2):
        """API-call for equipping a control with the attributes as defined in a
        json-file, representing a build tree. Useful to make it transparent in
        the code, that the attributes are added dynamically at runtime.
        """

        tree = Builder.getDict(tree)

        if level == 1:

            Builder.parseFields(tree["fields"], control)

        elif level == 2:

            Builder.parseBoxes(tree, control)

        elif level == 3:

            Builder.parseTabs(tree, control)

    def parseTabs(buildTree, control):
        """Propagates setAttributesFromJSON to all tabs.
        """

        for key in buildTree.keys():

            Builder.parseBoxes(buildTree[key]["content"], control)

    def parseBoxes(buildTree, control):
        """Propagates setAttributesFromJSON to all boxes.
        """

        for key in buildTree.keys():

            Builder.parseFields(buildTree[key]["fields"], control)

    def parseFields(buildTree, control):
        """Propagates setAttributesFromJSON to all fields.
        """

        for key in buildTree.keys():

            try:

                Builder.setAttributesField(key, control, buildTree[key]["default"])

            except AttributeError:

                pass

    def setAttributesField(identifier, control, default):
        """Sets the default value for control with attribute identifier.
        """

        try:

            return control.getCallbackDefault(identifier)(default)

        except AttributeError:

            return setattr(control, identifier, default)

    def buildTabs(buildTree, control):
        """Builds a tabbed layout from a level-3-buildtree.
        """

        layout = QVBoxLayout()

        tabs = QTabWidget()

        for key in buildTree.keys():

            title, content = Builder.extractTabData(**buildTree[key])

            tabLayout = Builder.buildBoxes(content, control)

            tab = QWidget()

            tab.setLayout(tabLayout)

            tabs.addTab(tab, title)

        layout.addWidget(tabs)

        return layout

    def buildBoxes(buildTree, control):
        """Builds a boxed layout from a level-2-buildtree.
        """

        layout = QVBoxLayout()

        boxLayout = None

        for key in buildTree:

            boxLayout = Builder.constructBoxLayout(buildTree[key], control)

            layout.addLayout(boxLayout)

        if boxLayout:
            boxLayout.addStretch()

        return layout

    def constructBoxLayout(box, control):
        """Constructs a box layout for a given box tree.
        """

        layout = QVBoxLayout()

        title = box['title']

        groupBox = QGroupBox(title)
        boxLayout = QVBoxLayout()

        fields = box['fields']

        for key in fields.keys():

            fieldLayout = Builder.constructFieldLayout(key, control, **fields[key])

            boxLayout.addLayout(fieldLayout)

        groupBox.setLayout(boxLayout)

        layout.addWidget(groupBox)

        return layout

    def constructFieldLayout(identifier, control, title, fieldType, default):
        """Constructs a box layout for a given field tree.
        """

        if type(fieldType) == str:
            fieldType = Builder.recoverBuiltInType(fieldType)

        widget = Builder.mapBuiltInTypeToWidget(fieldType)()

        Builder.setControlValue(widget, control, identifier, default)

        callback = Builder.getCallback(control, identifier, fieldType, widget)

        widget.valueChanged.connect(
            callback
        )

        return Builder.getLayoutForWidget(widget, title)

    def getCallback(control, identifier, fieldType, widget):
        """Gets the callback from the control if getCallback is implemented.
        Otherwise, setattr is the callback for this control.
        """

        try:

            return partial(control.getCallback(identifier), fieldType, widget)

        except AttributeError:

            return partial(Builder.callback(setattr), control, identifier, fieldType, widget)

    def setControlValue(widget, control, identifier, default):
        """If the control already has an attribute whose name is equal to the
        value of identifier, then the widget's value is set to the value of that
        attribute. Otherwise the attribute is created for that control and set
        to the default value.
        """

        try:

            widget.setValue(getattr(control, identifier))

        except AttributeError:

            widget.setValue(default)

            setattr(control, identifier, default)

    def getLayoutForWidget(widget, title):
        """Creates a horizontal ayout for a widget containing the widget itself and
        a descriptive title attached to it.
        """

        layout = QHBoxLayout()

        if not isinstance(widget, CustomQCheckBox):

            label = QLabel(title)
            layout.addWidget(label)
        else:

            widget.setText(title)

        layout.addWidget(widget)

        return layout

    def mapBuiltInTypeToWidget(fieldType):
        """Maps a list of built-in types to an appropriate widget type. Hence,
        the user can be agnostic of PyQt5 when using the builder, since only
        so many types are supported anyways. The custom widgets are wrappers
        around the original widgets to implement a unified interface
        """

        if fieldType == int:

            return CustomQSpinBox

        elif fieldType == float:

            return CustomQDoubleSpinBox

        elif fieldType == bool:

            return CustomQCheckBox

        elif fieldType == Builder.color:

            return CustomQColorPicker

        else:
            raise TypeError("Field type {} is not supported".format(str(fieldType)))

    def recoverBuiltInType(fieldType):
        """To support JSON input, builtin types must be recovered. However, for
        security reasons, it is best to use pydoc.locate, which recovers only
        builtin types from string, not functions or classes.
        Additionally supported are explicitly named strings which are checked
        before the locate call. The locate call returns None if the type does
        not exist.
        """

        if fieldType == 'color':
            return Builder.color

        return fieldType if type(fieldType) != str else locate(fieldType)


    def callback(function):
        """Decorator function for callback functions used in the build tree that
        precomputes the updated value and supplies it to the callback function.
        This serves PyQt5-agnositics with respect to the user.
        """

        def update(self, key, fieldType, widget):

            value = fieldType(widget.value())

            function(self, key, value)

        return update

    def getDict(tree):
        """If tree is a path, loads the corresponding file to a dict. Otherwise,
        return tree.
        """

        if type(tree) != dict:

            return Builder.loadJSON(tree)

        return tree

    def loadJSON(path):
        """Loads a JSON file into a dict type.
        """

        with codecs.open(path, 'r', 'utf8') as file:
            return json.load(file)

    def extractTabData(title, content):
        """Helper method to pass a dict as kwargs and return title and content
        from that dict. Works only if the format is valid.
        """

        return title, content

    def color(hexCode):
        """Used instead of a built-in type as fieldType.
        """

        return hexCode
