from PySide6.QtCore import Qt, QEvent, QRect
from PySide6.QtGui import QDoubleValidator, QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QTextEdit,
)


class TextInput(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        placeholder: str = None,
        default_text: str = None,
        validate_number=False,
        is_multiline=False,
    ):
        """
        Text input widget with label at the top and line edit below.

        Args:
            text (str, optional): label text. Defaults to None.
            placeholder (str, optional): placeholder for combobox. Defaults to None.
            validate_number (bool, optional): validate number after editing is finished?. Defaults to False.
        """
        super().__init__()
        self.validate_number = validate_number

        if self.validate_number and is_multiline:
            raise ValueError("Number validation is not supported for multiline input")

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(5)

        self.label = QLabel(self)

        if text is not None:
            self.label.setText(text)

        if is_multiline:
            self.text_input = ResizableTextEdit(self, visible_lines=3)
        else:
            self.text_input = QLineEdit(self)

        if default_text is not None:
            self.text_input.setText(default_text)

        if placeholder is not None:
            self.text_input.setPlaceholderText(placeholder)

        if self.validate_number:
            self._set_number_validator()

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.text_input)

    def get_value(self):
        """get value from line edit"""
        if self.validate_number:
            return float(self.text_input.text().replace(" ", "").replace(",", "."))

        if isinstance(self.text_input, QTextEdit):
            return self.text_input.toPlainText().strip()

        return self.text_input.text().strip()

    def clear(self):
        """clear line edit"""
        self.text_input.clear()

    def is_filled(self):
        """check if text input is filled"""
        if self.text_input.text() == "":
            return False
        return True

    def _set_number_validator(self):
        """Set number validator"""
        validator = QDoubleValidator(0, 999999999, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.text_input.setValidator(validator)
        self.text_input.editingFinished.connect(self._on_item_changed)

    def _on_item_changed(self):
        """
        Number formatter when editing is finished :
        - Thousand separator: space
        - Decimal separator: dot
        """
        item = self.text_input.text()
        try:
            # Cast to float
            number = float(item.replace(" ", "").replace(",", "."))
            if number.is_integer():
                formatted_number = f"{int(number):,}".replace(",", " ")
            else:
                formatted_number = f"{number:,.2f}".replace(",", " ").replace(
                    ".", ","
                )  # Format full decimal numbers

            self.text_input.setText(formatted_number)
        except ValueError:
            pass  # If it's not a valid integer, do nothing"


class ResizableTextEdit(QTextEdit):
    GRIP_SIZE = 12

    def __init__(self, parent=None, visible_lines=2):
        """
        Resizable text edit for longer text edits.
        On the right bottom corner button is placed with possibility to resize whole box

        Args:
            parent (_type_, optional): _description_. Defaults to None.
            visible_lines (int, optional): _description_. Defaults to 2.
        """
        super().__init__(parent)
        self._dragging = False
        self._visible_lines = visible_lines
        self._drag_start_y = 0
        self._start_height = 0
        self.viewport().installEventFilter(self)
        self._apply_initial_height()
        self.setObjectName("Description")

    def eventFilter(self, obj, event):
        """Event filtering"""
        if obj is not self.viewport():
            return super().eventFilter(obj, event)

        if event.type() == QEvent.Type.MouseButtonPress:
            if self._in_grip(event.position().toPoint()):
                self._dragging = True
                self._drag_start_y = event.globalPosition().toPoint().y()
                self._start_height = self.height()
                return True

        elif event.type() == QEvent.Type.MouseMove:
            if self._dragging:
                dy = event.globalPosition().toPoint().y() - self._drag_start_y
                new_h = max(self._min_height, self._start_height + dy)
                self.setFixedHeight(new_h)
                return True
            if self._in_grip(event.position().toPoint()):
                self.viewport().setCursor(Qt.CursorShape.SizeVerCursor)
            else:
                self.viewport().unsetCursor()

        elif event.type() == QEvent.Type.MouseButtonRelease:
            if self._dragging:
                self._dragging = False
                return True

        return super().eventFilter(obj, event)

    def _apply_initial_height(self):
        """Applying initial height for box"""
        self.ensurePolished()
        fm = self.fontMetrics()
        doc_margin = self.document().documentMargin()
        margins = self.contentsMargins()
        self._base_height = (
            fm.lineSpacing() * self._visible_lines
            + margins.top()
            + margins.bottom()
            + int(doc_margin * 2)
        )
        self._min_height = (
            fm.lineSpacing() * self._visible_lines
            + margins.top()
            + margins.bottom()
            + int(doc_margin * 2)
        )
        self.setFixedHeight(self._base_height)

    def _in_grip(self, pos):
        rect = self.viewport().rect()
        grip_rect = QRect(
            rect.right() - self.GRIP_SIZE,
            rect.bottom() - self.GRIP_SIZE,
            self.GRIP_SIZE,
            self.GRIP_SIZE,
        )
        return grip_rect.contains(pos)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.viewport().rect()
        grip_color = QColor("#bfbfbf")
        pen = QPen(grip_color, 1)
        painter.setPen(pen)

        # Three diagonal lines in bottom-right corner
        for i in range(3):
            offset = 4 + (i * 4)
            painter.drawLine(
                rect.right() - offset,
                rect.bottom(),
                rect.right(),
                rect.bottom() - offset,
            )

        painter.end()
