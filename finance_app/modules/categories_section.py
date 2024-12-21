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

    update_category = Signal(dict, str, str)

    def __init__(self, user_categories=None, user_categories_path=None) -> None:
        super().__init__()

        self.user_categories = user_categories
        self.user_categories_path = user_categories_path
        for key, value in self.user_categories.items():
            print(key, value, value.get("Level_1"), value.get("Level_2"))

        self.row_nums = (
            12 if self.user_categories is None else len(self.user_categories.keys())
        )

        self.add_category_window = None

        self.init_section()

    def init_section(self):
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
        print(data)
        print(pd.DataFrame(data).T.reset_index(drop=True))
        self.user_categories_table.clear_table()
        self.user_categories_table.update_table(
            pd.DataFrame(data).T.reset_index(drop=True)
        )
        self.user_categories = data

    def add_category(self):
        self.add_category_window = AddCategory()
        self.add_category_window.show()

        self.add_category_window.send_category.connect(self.get_category)

        print(self.add_category_window.category)

    @Slot(dict)
    def get_category(self, category):

        if self.user_categories is None:
            self.user_categories = {0: category}
        else:
            self.user_categories.update({len(self.user_categories.keys()): category})

        print(self.user_categories)
        with open(self.user_categories_path, "w") as file:
            json.dump(self.user_categories, file)

    def show_category(self, row, columns):
        name = self.user_categories_table.item(row, 4).text()
        level_1 = self.user_categories_table.item(row, 0).text()
        level_2 = self.user_categories_table.item(row, 1).text()
        level_3 = self.user_categories_table.item(row, 2).text()
        level_4 = self.user_categories_table.item(row, 3).text()

        selected_category = {
            key: val
            for key, val in self.user_categories.items()
            if filter_func(
                pair=val,
                condition=[level_1, level_2, level_3, level_4, name],
            )
        }
        tr_number = list(selected_category.keys())[0]

        self.category_edit = EditCategory(
            number=tr_number,
            name=name,
            level_1=level_1,
            level_2=level_2,
            level_3=level_3,
            level_4=level_4,
        )
        self.category_edit.show()

        self.category_edit.send_category.connect(self.get_category)

    @Slot(dict, str, str)
    def get_category(self, transaction, number, activity):
        self.update_category.emit(transaction, number, activity)
