from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame
from app.core.widgets.buttons import PushButton


class DueTile(QFrame):
    """
    Due tile is tile that shows number of due transaction with possibility to launch upcomings dialog.

    """
    review_signal = Signal()

    def __init__(self, due_count:int = 0, parent=None):
        super().__init__(parent=parent)

        self._due_count = due_count

        self.setObjectName("dueTile")
        self.setProperty("alert", "true" if self._due_count > 0 else "false")
        self.style().unpolish(self)
        self.style().polish(self)

        self.top_title = QLabel(self)
        self.top_title.setText("NEEDS ATTENTION")
        self.top_title.setObjectName("dueTileLabel")

        self.due_num_label = QLabel(self)
        self.due_num_label.setText("0 due")
        self.due_num_label.setObjectName("dueTileDueNum")
        self.due_num_label.setProperty("alert", "true" if self._due_count > 0 else "false")
        self.due_num_label.style().unpolish(self.due_num_label)
        self.due_num_label.style().polish(self.due_num_label)
        
        self.bottom_label = QLabel(self)
        self.bottom_label.setText("recurring transactions")
        self.bottom_label.setObjectName("dueTileBottom")

        self.review_btn = PushButton(
            text="Review",
            width=80,
            height=30,
            font_size=8,
            alternate_look=True,
            on_click=lambda: self.review_signal.emit()
        )
        self.review_btn.hide()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(self.top_title)
        main_layout.addWidget(self.due_num_label)
        main_layout.addWidget(self.bottom_label)
        main_layout.addWidget(self.review_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addStretch()

        self.set_data(self._due_count)


    def set_data(self, due_count:int):
        """Set's data"""
        self._due_count = due_count
        if self._due_count == 0:
            self.due_num_label.setText("All caught up")
            self.bottom_label.setText("no recurring transactions due")
            self.review_btn.hide()
        else:
            self.due_num_label.setText(f"{self._due_count} due")
            self.bottom_label.setText("recurring transactions")
            self.review_btn.show()

        self.due_num_label.setProperty("alert", "true" if self._due_count > 0 else "false")
        self.due_num_label.style().unpolish(self.due_num_label)
        self.due_num_label.style().polish(self.due_num_label)

        self.setProperty("alert", "true" if self._due_count > 0 else "false")
        self.style().unpolish(self)
        self.style().polish(self)
