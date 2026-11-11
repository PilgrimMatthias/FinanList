from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QPushButton,
    QButtonGroup,
    QVBoxLayout,
    QHBoxLayout,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics


class SegmentedControl(QWidget):

    value_changed = Signal(object)

    def __init__(
        self,
        parent=None,
        text: str = None,
        sub_text: str = None,
        end_text: str = None,
        values: list[tuple[any, str]] = [],
        default_value: any = None,
        label_position: str = "top",
        on_change=None,
    ):
        """
        Segmented selector - a pill track of mutually exclusive segments.

        Args:
            text (str, optional): text for label. Defaults to None.
            sub_text (str, optional): text for sub label. Defaults to None.
            end_text (str, optional): text shown after the track. Defaults to None.
            values (list, optional): list of (data, display_text) tuples. Defaults to [].
            default_value (any, optional): data of the segment to pre-select.
                Defaults to the first segment.
            label_position (str, optional): "top" stacks label and sub label above
                the track, "left" puts the label far left and the sub label beside
                the track. Defaults to "top".
            on_change (callable, optional): called with the selected data when the
                user picks a segment. Defaults to None.
        """
        super().__init__()

        self.values = values
        self.buttons = {}
        self.bold_reserved = False

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.label = QLabel(self)
        self.label.setObjectName("inputLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)
        self.label.hide()

        self.sub_label = QLabel(self)
        self.sub_label.setObjectName("inputSubLabel")
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setWordWrap(label_position != "left")
        self.sub_label.hide()

        self.end_label = QLabel(self)
        self.end_label.setObjectName("inputSubLabel")
        self.end_label.hide()

        if text is not None:
            self.label.setText(text)
            self.label.show()

        if sub_text is not None:
            self.sub_label.setText(sub_text)
            self.sub_label.show()

        if end_text is not None:
            self.end_label.setText(end_text)
            self.end_label.show()

        self.track = QFrame(self)
        self.track.setObjectName("segmentedTrack")

        self.track_layout = QHBoxLayout(self.track)
        self.track_layout.setContentsMargins(2, 2, 2, 2)
        self.track_layout.setSpacing(2)

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        # idClicked fires only on user interaction, so set_data() stays silent
        # without a blockSignals() dance.
        self.button_group.idClicked.connect(self.on_segment_clicked)

        self.add_items_with_data(items=values)

        if default_value is not None:
            self.set_data(default_value)
        elif values:
            self.set_data(values[0][0])

        if on_change is not None:
            self.value_changed.connect(on_change)

        self.build_layout(label_position)

    def add_items_with_data(self, items: list[tuple[any, str]]):
        """items is a list of (data, display_text) tuples."""
        self.values = items
        self.buttons = {}

        for index, (data, text) in enumerate(items):
            button = QPushButton(str(text), self.track)
            button.setObjectName("segmentButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            self.button_group.addButton(button, index)
            self.buttons[data] = button
            self.track_layout.addWidget(button)

    def build_layout(self, label_position: str):
        """Lay out the labels around the track."""
        centre = Qt.AlignmentFlag.AlignVCenter

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 10, 0, 10)
        self.widget_layout.setSpacing(5)

        if label_position == "left":
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(12)
            row.addWidget(self.label)
            row.addStretch(1)
            row.addWidget(self.sub_label)
            row.addWidget(self.track, 0, centre)
            row.addWidget(self.end_label, 0, centre)
            self.widget_layout.addLayout(row)
            return

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.sub_label)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self.track)
        row.addWidget(self.end_label, 0, centre)
        row.addStretch(1)
        self.widget_layout.addLayout(row)

    def get_value(self):
        """get display text of currently selected segment"""
        button = self.button_group.checkedButton()
        if button is None:
            return None
        return button.text()

    def get_data(self):
        """Returns the data of the currently selected segment."""
        button = self.button_group.checkedButton()
        if button is None:
            return None
        return self.values[self.button_group.id(button)][0]

    def set_value(self, value: str):
        """select a segment by its display text"""
        for data, text in self.values:
            if text == value:
                self.set_data(data)
                return

    def set_data(self, data):
        """select a segment by its data. unknown values are ignored"""
        button = self.buttons.get(data)
        if button is None or button.isChecked():
            return
        button.setChecked(True)

    def set_enabled_values(self, values: list):
        """grey out segments whose data is not in values"""
        allowed = set(values)
        for data, button in self.buttons.items():
            button.setEnabled(data in allowed)

    def set_text(self, text: str):
        self.update_label(self.label, text)

    def set_sub_text(self, text: str):
        self.update_label(self.sub_label, text)

    def set_end_text(self, text: str):
        self.update_label(self.end_label, text)

    def update_label(self, label: QLabel, text: str):
        """set a label's text and hide it when empty"""
        label.setText(text if text is not None else "")
        label.setVisible(bool(text))

    def is_filled(self):
        """check if a segment is selected"""
        return self.button_group.checkedButton() is not None

    def on_segment_clicked(self, index: int):
        self.value_changed.emit(self.values[index][0])

    def step(self, delta: int):
        """move the selection by delta, skipping disabled segments"""
        current = self.button_group.checkedId()
        if current < 0:
            return

        enabled = [
            index
            for index, (data, text) in enumerate(self.values)
            if self.buttons[data].isEnabled()
        ]
        if not enabled:
            return

        position = enabled.index(current) if current in enabled else 0
        target = enabled[max(0, min(len(enabled) - 1, position + delta))]

        if target != current:
            self.button_group.button(target).setChecked(True)
            self.value_changed.emit(self.values[target][0])

    def reserve_bold_width(self):
        """
        Stop the label clipping when :checked makes it bold.

        A segment's width comes from its size hint, computed at the unchecked
        font weight. If the stylesheet bolds the checked segment the text gets
        wider than the button and clips ("By category" -> "3y category").
        Reserve the difference once, after the stylesheet has been applied.
        """
        for button in self.buttons.values():
            bold = QFont(button.font())
            bold.setWeight(QFont.Weight.DemiBold)
            extra = QFontMetrics(bold).horizontalAdvance(
                button.text()
            ) - QFontMetrics(button.font()).horizontalAdvance(button.text())
            button.setMinimumWidth(button.sizeHint().width() + max(0, extra))

    def showEvent(self, event):
        super().showEvent(event)
        if not self.bold_reserved:
            self.bold_reserved = True
            self.reserve_bold_width()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Up):
            self.step(-1)
        elif event.key() in (Qt.Key.Key_Right, Qt.Key.Key_Down):
            self.step(1)
        elif event.key() == Qt.Key.Key_Home:
            self.step(-len(self.values))
        elif event.key() == Qt.Key.Key_End:
            self.step(len(self.values))
        else:
            super().keyPressEvent(event)
