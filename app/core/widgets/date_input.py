from PySide6.QtCore import QDate
from datetime import date
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QDateEdit


class DateInput(QWidget):
    def __init__(
        self,
        parent=None,
        text: str = None,
        on_date_change=None,
        nullable=False,
        placeholder="Select date",
        default_date: date = None,
    ):
        """
         Date input box with placeholder and label of the box.

        Args:
            text (str, optional): label of box. Defaults to None.
            on_date_change (_type_, optional): on date change function. Defaults to None.
            nullable (bool, optional): can date input be blank (null). Defaults to False.
            placeholder (str, optional): placeholder for nullabel box. Defaults to "Select date".
            default_date (date, optional): .default date to fill. Defaults to None,
        """
        super().__init__(parent)

        # Nullabel sets date input to optionally be blank
        self.nullable = nullable

        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(5)

        self.label = QLabel(self)
        if text is not None:
            self.label.setText(text)

        self.date_input = QDateEdit(self)
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy")

        if self.nullable:
            self.date_input.setMinimumDate(QDate(1900, 1, 1))
            self.date_input.setSpecialValueText(placeholder)
            self.date_input.setDate(self.date_input.minimumDate())
        else:
            self.date_input.setDate(QDate.currentDate())

        if default_date is not None:
            date = QDate.fromString(default_date, "yyyy-MM-dd")
            self.date_input.setDate(date)

        if on_date_change is not None:
            self.date_input.dateChanged.connect(on_date_change)

        self.widget_layout.addWidget(self.label)
        self.widget_layout.addWidget(self.date_input)

    def get_value(self) -> date | None:
        """Return selected date"""
        qdate = self.date_input.date()
        if self.nullable and qdate == self.date_input.minimumDate():
            return None
        return qdate.toPython()

    def set_date(self, value: date | None):
        """Set date for input"""
        if value is None and self.nullable:
            self.date_input.setDate(self.date_input.minimumDate())
        else:
            self.date_input.setDate(QDate(value.year, value.month, value.day))

    def clear(self):
        """Clear date input"""
        if self.nullable:
            self.date_input.setDate(self.date_input.minimumDate())
        else:
            self.date_input.setDate(QDate.currentDate())

    def is_filled(self):
        """check if text input is filled"""
        if self.date_input.date().toPython() is None:
            return False
        return True

    def set_label_text(self, text: str):
        """Update text above input"""
        self.label.setText(text)
