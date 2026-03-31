from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton


class UserProfileWidget(QWidget):
    def __init__(
        self,
        parent=None,
        initial: str = "",
        username: str = "+",
        on_click=None,
    ):
        """
        User profile widget - displayes username initials in circle button with username below.

        Args:
            initial (str, optional): letter to display in circle. Defaults to "".
            username (str, optional): name of the user to display below circle button. Defaults to "+".
            on_click (_type_, optional): on click method. Defaults to None.
        """
        super().__init__()
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setSpacing(5)
        self.widget_layout.setContentsMargins(10, 10, 10, 10)

        self.profile_btn = QPushButton(self)
        self.profile_btn.setText(initial)
        self.profile_btn.setFixedSize(160, 160)
        self.profile_btn.setObjectName("profileCircleButton")

        self.name_label = QLabel(self)
        self.name_label.setObjectName("profileNameLabel")
        self.name_label.setText(username)
        self.name_label.setFixedWidth(160)
        self.name_label.setStyleSheet("font-size: 18pt;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if on_click is not None:
            self.profile_btn.clicked.connect(on_click)

        self.widget_layout.addWidget(
            self.profile_btn, alignment=Qt.AlignmentFlag.AlignBottom
        )
        self.widget_layout.addWidget(
            self.name_label, alignment=Qt.AlignmentFlag.AlignTop
        )
