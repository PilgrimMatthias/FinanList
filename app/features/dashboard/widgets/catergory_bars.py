from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QVBoxLayout, QLabel, QFrame, QWidget, QHBoxLayout
from app.core.enums import Currency
from ..models import CategoryTotal
from app.core.widgets.color_picker import ColorCircle
from .category_bar_track import BarTrack
from app.core.enums import Currency
from app.core.utils import format_balance


class CategoryBars(QFrame):
    """
    Category bars creates widgets with 4 categories with top most spendings in a month.
    While 3 categories with most spendings are present, 4th is summed amount for the rest of categories.

    Args:
        QFrame (_type_): _description_
    """

    def __init__(self,parent=None, categories_total:list[CategoryTotal]=None, currency: Currency = Currency.PLN, month: str = ""):
        super().__init__(parent=parent)
        self.categories_total = categories_total
        self.currency = currency
        self.month = month

        self.setObjectName("categoryBars")

        top_row = QWidget(self)
        top_layout = QHBoxLayout(top_row)
        top_layout.setSpacing(5)
        top_layout.setContentsMargins(0,0,0,5)

        self.top_title = QLabel(self)
        self.top_title.setText("Spending by category")
        self.top_title.setObjectName("categoryBarsTitle")

        self.month_label = QLabel(self)
        self.month_label.setText("")
        self.month_label.setObjectName("categoryBarsMonth")

        self.total_label = QLabel(self)
        self.total_label.setText("")
        self.total_label.setObjectName("categoryBarsTotal")

        top_layout.addWidget(self.top_title)
        top_layout.addStretch()
        top_layout.addWidget(self.month_label)
        top_layout.addWidget(self.total_label)

        self.bottom_row = QWidget(self)
        self.bottom_layout = QVBoxLayout(self.bottom_row)
        self.bottom_layout.setSpacing(10)
        self.bottom_layout.setContentsMargins(0,0,0,0)

        self.empty_state_label = QLabel(self)
        self.empty_state_label.setText("No spending recorded this month")
        self.empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state_label.setObjectName("categoryBarsEmptyState")
        self.empty_state_label.hide()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(top_row)
        main_layout.addWidget(self.bottom_row, stretch=2)
        main_layout.addWidget(self.empty_state_label, stretch=2)
        # main_layout.addStretch()


    def set_data(self, categories_total: list[CategoryTotal], currency:Currency, month: str):
        """Updates data presented in ui"""
        self._clear()
        self.categories_total = categories_total
        self.currency = currency
        self.month = month

        total = 0

        if not categories_total:
            self.empty_state_label.show()
            self.bottom_row.hide()
        else:            
            self.empty_state_label.hide()
            self.bottom_row.show()

            for category_total in self.categories_total:
                temp_bar = self._create_bar(category_total=category_total)

                self.bottom_layout.addWidget(temp_bar)

                total += category_total.amount

        self.total_label.setText(f"{format_balance(total)} {self.currency.name}")
        self.month_label.setText(f"{self.month.capitalize()}")

    # Helpers
    def _clear(self):
        """Clear layout with bars"""
        while self.bottom_layout.count():
            item = self.bottom_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


    def _create_bar(self, category_total: CategoryTotal):
        """
        Create single category bard with it's name, progress bar and amount
        """
        bar_widget = QWidget()
        bar_layout = QHBoxLayout(bar_widget)
        bar_layout.setSpacing(5)
        bar_layout.setContentsMargins(0,0,0,0)

        circle_color = ColorCircle(color = category_total.color, size = 10)

        name_label = QLabel(self)
        name_label.setText(category_total.name)
        name_label.setContentsMargins(0,0,10,0)
        name_label.setMinimumWidth(150)
        name_label.setObjectName("categoryBarName")

        track = BarTrack(share=category_total.total_percentage, color=category_total.color)

        total_label = QLabel(self)
        total_label.setText(f"{format_balance(category_total.amount)}")
        total_label.setContentsMargins(10,0,0,0)
        total_label.setMinimumWidth(80)
        total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_label.setObjectName("categoryBarTotal")

        bar_layout.addWidget(circle_color)
        bar_layout.addWidget(name_label, alignment=Qt.AlignmentFlag.AlignLeft)
        bar_layout.addWidget(track, stretch=1)
        bar_layout.addWidget(total_label, alignment=Qt.AlignmentFlag.AlignRight)

        return bar_widget
