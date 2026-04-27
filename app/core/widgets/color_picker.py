from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt


from PySide6.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QLabel,
    QVBoxLayout,
    QColorDialog,
)

from .buttons import PushButton


class ColorCircle(QWidget):
    """
    Circle label with specified color inside

    Args:
        QWidget (_type_): _description_
    """

    def __init__(self, color: str = "#378ADD", size: int = 28, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color = QColor(color)

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()  # triggers repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self._color))
        painter.setPen(QPen(QColor(self._color), 1))
        painter.drawEllipse(1, 1, self.width() - 2, self.height() - 2)


class ColorPicker(QWidget):
    def __init__(
        self, parent=None, text: str = "Color", default_color: str = "#378ADD"
    ):
        super().__init__()

        self.color = "#378ADD"

        if default_color is not None:
            self.color = default_color

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(0)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        self.color_widget = QWidget()
        self.color_layout = QHBoxLayout(self.color_widget)
        self.color_layout.setSpacing(10)

        self.color_circle = ColorCircle(parent=self, color=self.color, size=30)

        self.color_name_label = QLabel(self)
        self.color_name_label.setText(self.color)
        self.color_name_label.setFixedHeight(30)
        self.color_name_label.setStyleSheet("color:#8d8b8b;")

        self.pick_btn = PushButton(
            text="Pick color",
            width=100,
            height=30,
            alternate_look=True,
            on_click=self._open_color_picker,
        )

        self.color_layout.addWidget(self.color_circle)
        self.color_layout.addWidget(self.color_name_label)
        self.color_layout.addWidget(self.pick_btn)
        self.color_layout.addStretch()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.color_widget)

    def _set_color(self, color: str):
        self.color = color
        self.color_circle.set_color(color)
        self.color_name_label.setText(color)

    def _open_color_picker(self):
        picker = QColorDialog(self)
        if self.color:
            picker.setCurrentColor(QColor(self.color))

        if picker.exec_():
            self._set_color(picker.currentColor().name())

    def get_color(self):
        return self.color

    def is_filled(self):
        return False if self.color is None or self.color == "" else True
