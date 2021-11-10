
from PyQt5.QtWidgets import QDialogButtonBox, QDialog
from sleepy.gui.builder import Builder
from sleepy import SLEEPY_ROOT_DIR
from sleepy.gui.settings._view import VIEW

class SettingsView(QDialog):

    def __init__(self, control, application):
        """View displaying the settings managed by an instance of :class:`Settings`.

        :param control: The instance of :class:`Settings` managing the settings.

        :param application: The calling application.
        """

        super().__init__(application)

        layout = Builder.build(VIEW, control, level = 3)

        layout.addStretch()

        layout.addWidget(self.__buildButtonBox(control))

        self.setLayout(layout)

    def __buildButtonBox(self, control):
        """Constructs a button box for the dialog.
        """

        buttonBox = QDialogButtonBox()
        buttonBox.addButton("Save", QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(control.update)
        buttonBox.accepted.connect(super().accept)

        buttonBox.addButton("Cancel", QDialogButtonBox.RejectRole)
        buttonBox.rejected.connect(control.reset)
        buttonBox.rejected.connect(super().reject)

        return buttonBox
