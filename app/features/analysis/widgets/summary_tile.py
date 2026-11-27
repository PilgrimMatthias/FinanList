from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout


class SummaryTile(QFrame):
    """One cell of the summary strip: caption, big number, hint line."""

    hint_clicked = Signal()

    def __init__(
        self,
        parent=None,
        text: str = None,
        value: str = "0,00",
        hint: str = None,
        hint_is_link=False,
        highlight=False,
    ):
        """
        Args:
            text (str, optional): caption above the number. Defaults to None.
            value (str, optional): the number, already formatted. Defaults to "0,00".
            hint (str, optional): small line under the number. Defaults to None.
            hint_is_link (bool, optional): render the hint as a clickable link
                and emit `hint_clicked`. Defaults to False.
            highlight (bool, optional): tag the tile with highlight="true" so the
                theme can lift it out of the row. Defaults to False.
        """
        super().__init__(parent)

        self.setObjectName("summaryTile")
        if highlight:
            self.setProperty("highlight", "true")

        self.label = QLabel(self)
        self.label.setObjectName("summaryLabel")

        self.value_label = QLabel(self)
        self.value_label.setObjectName("summaryValue")

        if hint_is_link:
            self.hint_label = QPushButton(self)
            self.hint_label.setObjectName("summaryLink")
            self.hint_label.setCursor(Qt.CursorShape.PointingHandCursor)
            self.hint_label.setFlat(True)
            self.hint_label.clicked.connect(self.hint_clicked)
        else:
            self.hint_label = QLabel(self)
            self.hint_label.setObjectName("summaryHint")

        if text is not None:
            self.label.setText(text)

        self.value_label.setText(value)
        self.set_hint(hint)

        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(16, 14, 16, 14)
        widget_layout.setSpacing(3)
        widget_layout.addWidget(self.label)
        widget_layout.addWidget(self.value_label)
        widget_layout.addWidget(self.hint_label)

    def set_value(self, value: str, tone: str = None):
        """Set the number. `tone` tags it for the theme (e.g. "danger")."""
        self.value_label.setText(value)
        self._set_tone(self.value_label, tone)

    def set_hint(self, text: str = None, tone: str = None):
        """Set the small line. Passing None hides it so the tile shrinks."""
        if not text:
            self.hint_label.setText("")
            self.hint_label.hide()
            return

        self.hint_label.setText(text)
        self._set_tone(self.hint_label, tone)
        self.hint_label.show()

    def _set_tone(self, widget, tone: str = None):
        """Swap the `tone` property and force QSS to re-evaluate."""
        if widget.property("tone") == tone:
            return

        widget.setProperty("tone", tone)
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
