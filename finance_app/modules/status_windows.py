from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ChooseBox(QDialog):
    """
    Window which gives opportunity to choose value from calue list and return it
    """

    def __init__(self, values, msg="Choose value!", parent=None):
        """_summary_

        Args:
            values (list): list to combobox
            msg (str, optional): Message for user. Defaults to "Choose value!".
            parent (_type_, optional): Defaults to None.
        """
        super().__init__(parent)

        # Choosen value
        self.selected_value = None

        # Window initialization with widgets
        self.setWindowTitle(msg)

        layout = QVBoxLayout()
        self.label = QLabel(msg)
        layout.addWidget(self.label)

        # Combo box with values list
        self.combo_box = QComboBox()
        self.combo_box.addItems(map(str, values))
        layout.addWidget(self.combo_box)

        # Confirm / Cancel boxes
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Button styllin
        self.button_box.setStyleSheet(
            "QPushButton {background-color: #5AC37D; border-style: solid; border-color: #5AC37D; border-width: 2px; border-radius: 10px; font-size: 11pt; width:80;} "
            + "QPushButton::pressed {background-color: #8fd6a7; border-style: solid; border-color: #8fd6a7; border-width: 2px; border-radius: 10px; font-size: 11pt;width:80px;}"
        )
        self.button_box.setMinimumHeight(30)
        self.button_box.setMinimumWidth(70)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def accept(self):
        """
        Accepting user choosen value
        """
        self.selected_value = str(self.combo_box.currentText())
        super().accept()

    def reject(self):
        """
        Canceling window and settting selected value to None.
        """
        self.selected_value = None
        super().reject()


class ErrorBox(QMessageBox):
    """
    Error box window which show message with provided title and msg.
    """

    def __init__(self, parent=None, title="Error", msg="Unknown error!"):
        super().__init__(parent)

        self.title = title
        self.msg = msg

        # Fonty
        self.font = QFont()
        self.font.setPointSize(11)

        self.init_box()

    def init_box(self):
        """
        Initialize error window
        """
        # Title and msg
        self.setWindowTitle(self.title)
        self.setText(self.msg)

        # Icon
        self.setIcon(QMessageBox.Critical)

        # Font for title and msg
        self.setFont(self.font)

        # Close button
        error_btn = QPushButton("Ok")
        error_btn.setStyleSheet(
            "QPushButton {background-color: #5AC37D; border-style: solid; border-color: #5AC37D; border-width: 2px; border-radius: 10px; font-size: 11pt;} "
            + "QPushButton::pressed {background-color: #8fd6a7; border-style: solid; border-color: #8fd6a7; border-width: 2px; border-radius: 10px; font-size: 11pt;}"
        )
        error_btn.setMinimumHeight(30)
        error_btn.setMinimumWidth(70)

        self.addButton(error_btn, QMessageBox.AcceptRole)

        # Show button
        self.exec()
