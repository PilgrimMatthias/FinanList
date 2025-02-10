from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd

from finance_app.config import *
from finance_app.modules import (
    AddCategory,
    TableWidget,
    EditCategory,
    ErrorBox,
    filter_func,
)


class CategoriesSection(QWidget):

    update_category = Signal(
        dict, list, str
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

        # Select upcomings btn
        self.select_btn = QPushButton("Select")
        self.select_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.select_btn.setMinimumHeight(40)
        self.select_btn.setMinimumWidth(130)
        self.select_btn.clicked.connect(self.on_select_click)

        # Delete categories btn
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(
            "QPushButton {background-color: #ff3333; border-style: solid; border-color: #ff3333; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #ff8080; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setMinimumWidth(130)
        self.delete_btn.setVisible(False)
        self.delete_btn.clicked.connect(self.delete_categories)

        btn_layout.addWidget(self.add_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.select_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.delete_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)

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
            id_column=True,
        )
        self.user_categories_table.cellDoubleClicked.connect(self.show_category)

        main_layout.addLayout(btn_layout, 0)
        main_layout.addWidget(self.user_categories_table, 0)

    def on_select_click(self):
        """
        On select button click event.

        When clicked delete button and first id column is shown/hidden.
        """
        # Show/hide id column in table
        self.user_categories_table.show_column(0)

        # Show/hide delete button
        if self.delete_btn.isVisible():
            self.delete_btn.setVisible(False)
        else:
            self.delete_btn.setVisible(True)

    def delete_categories(self):
        """
        Delete categories event

        When clicked selected categories by user will be deleted from database.
        """
        # Selected rows
        selected_rows = self.user_categories_table.get_selected_rows()

        if len(selected_rows) == 0:
            msg = "No categories where selected!\nSelect at least one category!"
            ErrorBox(self, title="Nothing to delete!", msg=msg)
            return

        # Deletion confirmation box
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Delete selected categories?\nThis will permamently delete them!",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            # Create transation dicts
            selected_cat_dict = {}
            for tr_num in selected_rows:
                temp_category = self.user_categories.get(str(tr_num))

                selected_cat_dict[str(tr_num)] = temp_category

            # Send transactions to delete
            self.update_category.emit(
                selected_cat_dict, list(selected_cat_dict.keys()), "Delete"
            )

    def update_categories(self, data):
        """
        Update categories database and values in table

        Args:
            data (dict): category dict list
        """
        self.user_categories = data
        self.user_categories_table.clear_table()

        if len(self.user_categories) > 0:
            updated_df = pd.DataFrame(data).T.reset_index(drop=True)
            updated_df.columns = CATEGORIES_HEADERS
            self.user_categories_table.update_table(updated_df)

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
        tr_number = (
            self.user_categories_table.cellWidget(row, 0)
            .findChild(QCheckBox)
            .get_hidden_property()
        )
        name = self.user_categories_table.item(row, 4).text()
        main_category = self.user_categories_table.item(row, 1).text()
        subcategory = self.user_categories_table.item(row, 2).text()
        def_oper_type = self.user_categories_table.item(row, 3).text()

        self.category_edit = EditCategory(
            number=tr_number,
            name=name,
            main_category=main_category,
            subcategory=subcategory,
            def_oper_type=def_oper_type,
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
        self.update_category.emit(transaction, [number], activity)
