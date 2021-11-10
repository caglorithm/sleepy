
from PyQt5.QtWidgets import QCheckBox, QDoubleSpinBox, QSpinBox, QLineEdit, QPushButton, QHBoxLayout, QWidget, QColorDialog
from PyQt5.QtCore import Qt

class CustomQColorPicker(QWidget):
    """Custom widget displaying a QLineEdit and a colored button. The user can
    choose a color or enter a hex-value.
    """

    def __init__(self):

        super().__init__()

        self.colorCode = QLineEdit()
        self.button = QPushButton('')
        self.button.clicked.connect(self.onClick)
        self.button.setMaximumHeight(20)
        self.button.setMaximumWidth(20)

        layout = QHBoxLayout()

        layout.addWidget(self.colorCode, alignment = Qt.AlignRight)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def onClick(self, event):
        """Displays a Qt color dialog. The selected color is stored in the
        QLineEdit.
        """

        self.setValue(QColorDialog.getColor().name())

    def setValue(self, value):
        """Set the value of the QLineEdit to a given input value.
        """

        self.colorCode.setText(value.upper())

        stylesheet = "QPushButton { background: %s; }" % value.upper()

        self.button.setStyleSheet(
            stylesheet
        )

    def value(self):
        """Returns the hex code of the color selected.
        """

        return self.colorCode.text()

    @property
    def valueChanged(self):
        """Returns an event slot for valueChanged. Corresponds to the textChanged
        event slot of the QLineEdit.
        """

        return self.colorCode.textChanged

class CustomQCheckBox(QCheckBox):
    """Wrapper around QCheckBox to give it a unified interface.
    """

    def setValue(self, value):
        """Wrapper around the value setter of the internal widget.
        """

        self.setChecked(bool(value))

    def value(self):
        """Wrapper around the value getter of the internal widget.
        """

        return int(self.isChecked())

    @property
    def valueChanged(self):
        """Wrapper around the value change event of the internal widget.
        """

        return self.stateChanged

class CustomQDoubleSpinBox(QDoubleSpinBox):
    """Wrapper around QDoubleSpinBox to give it a unified interface.
    """

    def __init__(self):

        super().__init__()

        self.setMinimum(0.0)
        self.setMaximum(100.0)

    def setValue(self, value):
        """Wrapper around the value setter of the internal widget.
        """

        super().setValue(float(value))

class Custom0To1DoubleSpinBox(CustomQDoubleSpinBox):
    """Wrapper around CustomQDoubleSpinBox to accept only values between 0 and 1.
    """

    def __init__(self):

        super().__init__()

        self.setMinimum(0.0)
        self.setMaximum(1.0)

class CustomQSpinBox(QSpinBox):
    """Wrapper around QSpinBox to give it a unified interface.
    """

    def setValue(self, value):
        """Wrapper around the value setter of the internal widget.
        """

        super().setValue(int(value))
