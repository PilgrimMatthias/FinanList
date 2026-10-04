from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QFrame, QWidget
from ..models import MonthSummary
from app.core.widgets.line_frames import HLine
from app.core.utils import format_balance



class MonthTile(QFrame):
    """
    Month tile presents current month income and outgoing amount with net calculation.

    """
    def __init__(self, current_month:str = "", month_summary: MonthSummary = None, parent = None):
        super().__init__(parent)
        self.month_summary = month_summary or MonthSummary()
        self.current_month = current_month

        self.setObjectName("monthTile")    

        self.month_label = QLabel(self)
        self.month_label.setText(f"{self.current_month.upper()} SO FAR")
        self.month_label.setObjectName("monthTileTopLabel")

        # Income widget
        income_widget = QWidget(self)
        income_layout = QHBoxLayout(income_widget)
        income_layout.setSpacing(0)
        income_layout.setContentsMargins(0,0,0,0)

        income_label = QLabel(self)
        income_label.setText("Income")
        income_label.setObjectName("monthTileMiddleLabel")

        self.income_amount_label = QLabel(self)
        self.income_amount_label.setText(f"+{format_balance(self.month_summary.income)}")
        self.income_amount_label.setObjectName("monthTileIncome")

        income_layout.addWidget(income_label)
        income_layout.addStretch()
        income_layout.addWidget(self.income_amount_label)

        # Expenses widget
        expenses_widget = QWidget(self)
        expenses_layout = QHBoxLayout(expenses_widget)
        expenses_layout.setSpacing(0)
        expenses_layout.setContentsMargins(0,0,0,0)

        expenses_label = QLabel(self)
        expenses_label.setText("Outgoing")
        expenses_label.setObjectName("monthTileMiddleLabel")

        self.expenses_amount_label = QLabel(self)
        self.expenses_amount_label.setText(f"-{format_balance(self.month_summary.outgoing)}")
        self.expenses_amount_label.setObjectName("monthTileExpense")

        expenses_layout.addWidget(expenses_label)
        expenses_layout.addStretch()
        expenses_layout.addWidget(self.expenses_amount_label)

        # Net widget
        net_widget = QWidget(self)
        net_layout = QHBoxLayout(net_widget)
        net_layout.setSpacing(0)
        net_layout.setContentsMargins(0,0,0,0)

        net_label = QLabel(self)
        net_label.setText("Net")
        net_label.setObjectName("monthTileBottomLabel")

        self.net_amount_label = QLabel(self)
        sign = "+" if self.month_summary.net >= 0 else "-"
        self.net_amount_label.setText(f"{sign}{format_balance(self.month_summary.net)}")
        self.net_amount_label.setProperty("positive", "true" if self.month_summary.net >= 0 else "false")
        self.net_amount_label.style().unpolish(self.net_amount_label)
        self.net_amount_label.style().polish(self.net_amount_label)
        self.net_amount_label.setObjectName("monthTileNet")

        net_layout.addWidget(net_label)
        net_layout.addStretch()
        net_layout.addWidget(self.net_amount_label)

        h_line = HLine()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(self.month_label)
        main_layout.addWidget(income_widget)
        main_layout.addWidget(expenses_widget)
        main_layout.addWidget(h_line)
        main_layout.addWidget(net_widget)
        main_layout.addStretch()

    def set_data(self, current_month:str = None, month_summary: MonthSummary = None):
        """Set's data in ui"""
        if current_month is not None:
            self.current_month = current_month
            self.month_label.setText(f"{self.current_month.upper()} SO FAR")

        if month_summary is not None:
            self.month_summary = month_summary
            self.income_amount_label.setText(f"+{format_balance(self.month_summary.income)}")
            self.expenses_amount_label.setText(f"-{format_balance(self.month_summary.outgoing)}")

            sign = "+" if self.month_summary.net >= 0 else "-"
            self.net_amount_label.setText(f"{sign}{format_balance(self.month_summary.net)}")
            self.net_amount_label.setProperty("positive", "true" if self.month_summary.net >= 0 else "false")
            self.net_amount_label.style().unpolish(self.net_amount_label)
            self.net_amount_label.style().polish(self.net_amount_label)
