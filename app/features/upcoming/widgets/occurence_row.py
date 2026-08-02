import math
from datetime import datetime
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QCheckBox, QLabel
from app.database import Transaction

class OccurenceRow(QWidget):
    """
    Single occcurence row which displayes transaction date with possibility to check it for confirmation in database
    """
    selection_changed = Signal()

    def __init__(self, transaction: Transaction, parent=None):
        super().__init__(parent)

        self.transaction = transaction

        self.checkbox_widget = QCheckBox(self)
        self.checkbox_widget.setChecked(False)
        self.checkbox_widget.checkStateChanged.connect(self._on_check)

        
        self.date_label = QLabel(self)
        self.date_label.setObjectName("occurrenceDate")
        self.date_label.setText(self.transaction.date.strftime("%d.%m.%Y")) # assuming date is datetime
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.timeline_label = QLabel(self)
        self.timeline_label.setObjectName("occurrenceTimeline")
        
        self.timeline_label.setText(self._set_timeline(self.transaction.date))
        self.timeline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)


        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(15, 0, 0, 0)

        main_layout.addWidget(self.checkbox_widget)
        main_layout.addWidget(self.date_label)
        main_layout.addStretch()
        main_layout.addWidget(self.timeline_label)

    def _set_timeline(self, date:str) -> str:
        """Sets timeline text for transactions - today minus transaction date"""
        today = datetime.today()

        difference = today - date

        self.timeline_label.setProperty("overdue", "true" if difference.days > 30 else "false")

        if difference.days == 0:
            return "today"
        elif difference.days == 1:
            return "yesterday"
        elif difference.days < 30:
            return f"{difference.days} days ago"
        elif difference.days/365 < 1:
            timeline_text = ""

            months = math.floor(difference.days/30)
            days_left = difference.days - months * 30

            # months
            timeline_text =  f"{months} months"
            if months == 1:
                timeline_text = f"{months} month"

            # days
            if days_left > 0:
                timeline_text += " {0} {1} ago".format(days_left, "day" if days_left == 1 else "days")
            else:
                timeline_text += " ago"

            return timeline_text
        else:
            timeline_text = ""

            years = math.floor(difference.days/365)
            months =  math.floor((difference.days - years * 365)/30)
            days = difference.days - years * 365 - months * 30

            # years
            timeline_text =  f"{years} years"
            if years == 1:
                timeline_text = f"{years} year"

            # months
            if months == 0:
                timeline_text += ""
            elif months == 1:
                timeline_text += f" {months} month"
            else: 
                timeline_text +=  f" {months} months"

            # days
            if days > 0:
                timeline_text += " {0} {1} ago".format(days, "day" if days == 1 else "days")
            else:
                timeline_text += " ago"

            return timeline_text
        
    def get_transaction(self) -> Transaction:
        """Returns transactions"""
        return self.transaction 
        
    def is_checked(self):
        """Check if chekcbox is checked"""
        return self.checkbox_widget.isChecked()

    def set_checked(self, checked:bool = False):
        """Sets checkbox state"""
        self.checkbox_widget.setChecked(checked)

    def _on_check(self):
        """On check sends signal"""
        self.selection_changed.emit()



