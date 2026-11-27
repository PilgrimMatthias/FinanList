from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QButtonGroup,
    QHBoxLayout,
)


class TabBar(QWidget):
    """A row of underlined tabs."""

    value_changed = Signal(object)

    def __init__(
        self,
        parent=None,
        values: list[tuple] = [],
        default_value=None,
        on_change=None,
    ):
        """
        Args:
            values (list, optional): list of (data, display_text) tuples.
                Defaults to [].
            default_value (any, optional): data of the tab to pre-select.
                Defaults to the first tab.
            on_change (callable, optional): called with the selected data
                when the user picks a tab. Defaults to None.
        """
        super().__init__(parent)

        self.values = values
        self.buttons = {}
        self.bold_reserved = False

        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        # idClicked fires only on user interaction, so set_data() stays
        # silent and cannot loop back into the view that called it.
        self.button_group.idClicked.connect(self.on_tab_clicked)

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_layout.setSpacing(4)

        self.add_items_with_data(values)

        if values:
            self.set_data(default_value if default_value is not None else values[0][0])

        if on_change is not None:
            self.value_changed.connect(on_change)

    def add_items_with_data(self, items: list[tuple]):
        """items is a list of (data, display_text) tuples."""
        for button in self.buttons.values():
            self.button_group.removeButton(button)
            self.widget_layout.removeWidget(button)
            button.deleteLater()

        self.values = items
        self.buttons = {}

        for index, (data, text) in enumerate(items):
            button = QPushButton(str(text), self)
            button.setObjectName("viewTab")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            self.button_group.addButton(button, index)
            self.buttons[data] = button
            self.widget_layout.addWidget(button)

        # No trailing stretch: the bar is only as wide as its tabs, so the
        # owner's layout decides where it sits (right-aligned in Analysis).

    def get_data(self):
        """Returns the data of the currently selected tab."""
        button = self.button_group.checkedButton()
        if button is None:
            return None
        return self.values[self.button_group.id(button)][0]

    def set_data(self, data):
        """Select a tab by its data. Unknown values are ignored."""
        button = self.buttons.get(data)
        if button is None or button.isChecked():
            return
        button.setChecked(True)

    def on_tab_clicked(self, index: int):
        self.value_changed.emit(self.values[index][0])

    def reserve_bold_width(self):
        """Stop the label clipping when :checked makes it bold."""
        for button in self.buttons.values():
            bold = QFont(button.font())
            bold.setWeight(QFont.Weight.DemiBold)
            extra = QFontMetrics(bold).horizontalAdvance(button.text()) - QFontMetrics(
                button.font()
            ).horizontalAdvance(button.text())
            button.setMinimumWidth(button.sizeHint().width() + max(0, extra))

    def showEvent(self, event):
        super().showEvent(event)
        if not self.bold_reserved:
            self.bold_reserved = True
            self.reserve_bold_width()
