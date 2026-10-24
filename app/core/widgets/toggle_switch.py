from PySide6.QtCore import Qt, Signal, QRectF
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout

from app.core.theme.palette import Palette, palette_signals


class ToggleSwitch(QWidget):
    """Pill toggle switch."""

    toggled = Signal(bool)

    TRACK_W = 44
    TRACK_H = 22
    KNOB = 18
    PADDING = 2

    def __init__(self, checked: bool = False, parent=None):
        super().__init__(parent)
        self._checked = checked

        self.setFixedSize(self.TRACK_W, self.TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        palette_signals.changed.connect(self._on_palette_changed)

    # State
    def is_checked(self) -> bool:
        return self._checked

    def set_checked(self, checked: bool, emit: bool = False):
        """Set state. Silent by default - a view filling fields during reload
        should not trigger the same handler a user click would."""
        if self._checked == checked:
            return
        self._checked = checked
        self.update()
        if emit:
            self.toggled.emit(self._checked)

    def toggle(self):
        self._checked = not self._checked
        self.update()
        self.toggled.emit(self._checked)

    # Interaction
    def mouseReleaseEvent(self, event):
        if not self.isEnabled():
            return
        if event.button() != Qt.MouseButton.LeftButton:
            return
        # Press-then-drag-away-then-release should not fire.
        if not self.rect().contains(event.position().toPoint()):
            return
        self.toggle()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self.isEnabled():
                self.toggle()
            return
        super().keyPressEvent(event)

    # Painting
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        if not self.isEnabled():
            track_key = "text_disabled"
        else:
            track_key = "toggle_on" if self._checked else "toggle_off"

        radius = self.TRACK_H / 2
        track = QRectF(0, 0, self.TRACK_W, self.TRACK_H)
        painter.setBrush(Palette.color(track_key))
        painter.drawRoundedRect(track, radius, radius)

        knob_x = (
            self.TRACK_W - self.KNOB - self.PADDING
            if self._checked
            else self.PADDING
        )
        knob_y = (self.TRACK_H - self.KNOB) / 2
        painter.setBrush(Palette.color("toggle_knob"))
        painter.drawEllipse(QRectF(knob_x, knob_y, self.KNOB, self.KNOB))

        # Focus ring - keyboard users need to see where they are
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            pen = painter.pen()
            pen.setStyle(Qt.PenStyle.SolidLine)
            pen.setWidth(1)
            pen.setColor(Palette.color("accent"))
            painter.setPen(pen)
            painter.drawRoundedRect(track.adjusted(0.5, 0.5, -0.5, -0.5), radius, radius)

    def _on_palette_changed(self, theme: str):
        self.update()


class SwitchInput(QWidget):
    """Labelled switch"""

    def __init__(
        self,
        parent=None,
        text: str = None,
        sub_text: str = None,
        default_value: bool = False,
        on_change=None,
    ):
        """
        Args:
            text (str, optional): label text. Defaults to None.
            sub_text (str, optional): muted explanatory line under the label.
            default_value (bool, optional): initial state. Defaults to False.
            on_change (optional): called with the new bool when the user toggles.
        """
        super().__init__(parent)

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(10)

        label_widget = QWidget(self)
        label_layout = QVBoxLayout(label_widget)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(2)

        self.label = QLabel(self)
        self.label.setObjectName("inputLabel")

        self.sub_label = QLabel(self)
        self.sub_label.setObjectName("inputSubLabel")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.sub_label.hide()

        if text is not None:
            self.label.setText(text)

        if sub_text is not None:
            self.sub_label.setText(sub_text)
            self.sub_label.show()

        label_layout.addWidget(self.label)
        label_layout.addWidget(self.sub_label)

        self.switch = ToggleSwitch(checked=default_value)

        if on_change is not None:
            self.switch.toggled.connect(on_change)

        self.widget_layout.addWidget(label_widget)
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(
            self.switch, alignment=Qt.AlignmentFlag.AlignVCenter
        )

    def get_value(self) -> bool:
        """Current state."""
        return self.switch.is_checked()

    def set_value(self, value: bool, emit: bool = False):
        """Set state without firing on_change, so a reload cannot write back the value it just read."""
        self.switch.set_checked(value, emit=emit)

    def set_enabled(self, enabled: bool):
        self.switch.setEnabled(enabled)
        self.label.setEnabled(enabled)
        self.sub_label.setEnabled(enabled)
        self.switch.update()