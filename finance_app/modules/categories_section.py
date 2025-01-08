from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd

from finance_app.widgets.table_widget import TableWidget
from finance_app.modules.add_windows import EditCategory
from finance_app.config import *
from finance_app.utils import filter_func

from finance_app.modules.add_windows import AddCategory


class CategoriesSection(QWidget):

    update_category = Signal(
        dict, str, str
    )  # signal for category operation on database

    def __init__(self, user_categories=None, user_categories_path=None) -> None:
        super().__init__()

        self.user_categories = user_categories
        self.user_categories_path = user_categories_path

        self.row_nums = (
            12 if self.user_categories is None else len(self.user_categories.keys())
        )

        self.add_category_window = None

        self.init_section()

    def init_section(self):
        """
        Section initialization
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(15)

        # Title layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Add category btn
        self.add_btn = QPushButton("Add category")
        self.add_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setMinimumWidth(130)
        self.add_btn.clicked.connect(self.add_category)

        # Edit category btn
        self.edit_btn = QPushButton("Edit categories")
        self.edit_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setMinimumWidth(130)

        btn_layout.addWidget(self.add_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        # btn_layout.addWidget(self.edit_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        # Table with categories
        self.user_categories_table = TableWidget(
            parent=self,
            row_num=self.row_nums,
            col_num=len(CATEGORIES_HEADERS),
            header_names=CATEGORIES_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            data=(
                None
                if self.user_categories is None
                else pd.DataFrame(self.user_categories).T.reset_index(drop=True)
            ),
            sorting=True,
        )
        self.user_categories_table.cellDoubleClicked.connect(self.show_category)

        main_layout.addLayout(btn_layout, 0)
        main_layout.addWidget(self.user_categories_table, 0)

    def update_categories(self, data):
        """
        Update categories database and values in table

        Args:
            data (dict): category dict list
        """
        updated_df = pd.DataFrame(data).T.reset_index(drop=True)
        updated_df.columns = CATEGORIES_HEADERS

        self.user_categories_table.clear_table()
        self.user_categories_table.update_table(updated_df)
        self.user_categories = data

    def add_category(self):
        """
        Invoke new category window
        """
        self.add_category_window = AddCategory()
        self.add_category_window.show()

        self.add_category_window.send_category.connect(self.get_new_category)

    @Slot(dict)
    def get_new_category(self, category):
        """
        Send new category to update in database and and section

        Args:
            category (dict): new category
        """
        self.send_category(
            transaction=category,
            number=(
                "0"
                if self.user_categories is None
                else str(len(self.user_categories.keys()))
            ),
            activity="New",
        )

    def show_category(self, row, columns):
        """
        Show choosen category from list for user

        Args:
            row (int): row of category in table
            columns (int): column of ctaegory in table
        """
        name = self.user_categories_table.item(row, 3).text()
        main_category = self.user_categories_table.item(row, 0).text()
        subcategory = self.user_categories_table.item(row, 1).text()
        def_oper_type = self.user_categories_table.item(row, 2).text()
        # level_4 = self.user_categories_table.item(row, 3).text()

        selected_category = {
            key: val
            for key, val in self.user_categories.items()
            if filter_func(
                pair=val,
                condition=[main_category, subcategory, def_oper_type, name],
                # condition=[main_category, subcategory, def_oper_type, level_4, name],
            )
        }
        tr_number = list(selected_category.keys())[0]

        self.category_edit = EditCategory(
            number=tr_number,
            name=name,
            main_category=main_category,
            subcategory=subcategory,
            def_oper_type=def_oper_type,
            # level_4=level_4,
        )
        self.category_edit.show()

        self.category_edit.send_category.connect(self.send_category)

    @Slot(dict, str, str)
    def send_category(self, transaction, number, activity):
        """
        Emit signal with category to update and it's number and activity for database.

        Args:
            transaction (dict): category dict with information
            number (int): number of category in database (new or existing)
            activity (str): type of acitivty (New, Delete or Update)
        """
        self.update_category.emit(transaction, number, activity)
