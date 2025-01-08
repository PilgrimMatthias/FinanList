from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from datetime import datetime

from finance_app.config import *
from finance_app import center_window, ChooseBox


class AddCategory(QWidget):
    """

    AddCategory creates new window with option to add new category to transasctions
    """

    send_category = Signal(dict)

    def __init__(self):
        super().__init__()

        self.category = None

        self.init_window()

    def init_window(self):
        """
        New category window initialization
        """
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        self.setContentsMargins(15, 5, 15, 5)
        self.resize(QSize(500, 300))
        self.setFixedSize(QSize(400, 325))
        main_layout.setSpacing(10)

        # Title label
        self.title_label = QLabel(self)
        self.title_label.setText("New Category")
        self.title_label.setStyleSheet(
            "color: black; font-size: 16pt; padding:5px; font-weight:bold;"
        )
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Custom name - label
        self.custom_name_label = QLabel(self)
        self.custom_name_label.setText("Name of category")
        self.custom_name_label.setStyleSheet("color: black; font-size: 12pt;")
        self.custom_name_label.setWordWrap(True)
        self.custom_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Custom name - lineedit
        self.custom_name_edit = QLineEdit(self)
        self.custom_name_edit.setStyleSheet("background-color: #e6e6e6")
        self.custom_name_edit.setEnabled(False)

        # Top level - label
        self.main_category_label = QLabel(self)
        self.main_category_label.setText("Main Category")
        self.main_category_label.setStyleSheet("color: black; font-size: 12pt;")
        self.main_category_label.setWordWrap(True)
        self.main_category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Top level - lineedit
        self.main_category__edit = QLineEdit(self)

        # Second level - label
        self.subcategory_label = QLabel(self)
        self.subcategory_label.setText("Subcategory")
        self.subcategory_label.setStyleSheet("color: black; font-size: 12pt;")
        self.subcategory_label.setWordWrap(True)
        self.subcategory_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Second level - lineedit
        self.subcategory_edit = QLineEdit(self)

        # Third level - label
        self.def_oper_type_label = QLabel(self)
        self.def_oper_type_label.setText("Default operation type")
        self.def_oper_type_label.setStyleSheet("color: black; font-size: 12pt;")
        self.def_oper_type_label.setWordWrap(True)
        self.def_oper_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Third level - lineedit
        self.def_oper_type_edit = QComboBox(self)
        self.def_oper_type_edit.addItems(TRANSACTION_TYPES)

        self.main_category__edit.editingFinished.connect(self.on_value_changed)
        self.subcategory_edit.editingFinished.connect(self.on_value_changed)

        # Add button
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 20, 0, 0)

        self.primary_btn = QPushButton("Add")
        self.primary_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.primary_btn.setMinimumHeight(40)
        self.primary_btn.setMinimumWidth(130)
        self.primary_btn.clicked.connect(self.create_category)

        # Cancel button
        self.secondary_btn = QPushButton("Cancel")
        self.secondary_btn.setStyleSheet(
            "QPushButton {background-color: #ff0000; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #ff8080; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.secondary_btn.setMinimumHeight(40)
        self.secondary_btn.setMinimumWidth(130)
        self.secondary_btn.clicked.connect(self.destroy)

        btn_layout.addWidget(self.primary_btn, 0)
        btn_layout.addWidget(self.secondary_btn, 0)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff0000;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff8080;}"
        )
        self.close_btn.setMinimumHeight(40)
        self.close_btn.setMinimumWidth(130)
        self.close_btn.clicked.connect(self.destroy)
        self.close_btn.setVisible(False)

        # Spacer for bottom
        self.spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(
            self.title_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(self.custom_name_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.custom_name_edit, 1, 1)

        main_layout.addWidget(
            self.main_category_label, 2, 0, Qt.AlignmentFlag.AlignLeft
        )
        main_layout.addWidget(self.main_category__edit, 2, 1)

        main_layout.addWidget(self.subcategory_label, 3, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.subcategory_edit, 3, 1)

        main_layout.addWidget(
            self.def_oper_type_label, 4, 0, Qt.AlignmentFlag.AlignLeft
        )
        main_layout.addWidget(self.def_oper_type_edit, 4, 1)

        main_layout.addLayout(btn_layout, 5, 0, 1, 2)
        main_layout.addWidget(self.close_btn, 6, 0, Qt.AlignmentFlag.AlignLeft)

        main_layout.addItem(self.spacer)

    def on_value_changed(self):
        """
        Set category custom name as every level widget text separated with "-"
        """
        cat_name = ""
        for widget in [self.main_category__edit, self.subcategory_edit]:
            if widget.text():
                cat_name += widget.text() + " - "

        cat_name = cat_name[:-3]

        self.custom_name_edit.setText(cat_name)

    def create_category(self):
        """
        Method used for sending new category dict based on user inputs
        """
        self.category = {
            "Name": self.custom_name_edit.text(),
            "1_Main Category": self.main_category__edit.text(),
            "2_Subcategory": self.subcategory_edit.text(),
            "3_Default Operation Type": self.def_oper_type_edit.currentText(),
        }

        self.send_category.emit(self.category)

        self.destroy()


class EditCategory(AddCategory):
    """
    EditCategory creates window with option to edit choosen category.

    EditCategory inherites AddCategory class
    """

    send_category = Signal(dict, str, str)

    def __init__(
        self,
        number,
        name,
        main_category,
        subcategory,
        def_oper_type,
    ):
        super().__init__()

        # Category data
        self.number = number
        self.name = name
        self.main_category = main_category
        self.subcategory = subcategory
        self.def_oper_type = def_oper_type

        self.active = False

        # Changes in layout of AddCategory
        self.primary_btn.clicked.disconnect()
        self.primary_btn.clicked.connect(self.edit_category)
        self.secondary_btn.clicked.connect(self.delete_category)
        self.close_btn.setVisible(True)
        self.close_btn.clicked.connect(self.close_event)
        self.setFixedSize(QSize(400, 375))
        self.fill_widgets()

    def fill_widgets(self):
        """
        Method used for filling widget with choosen category data
        """
        # Filling data
        self.title_label.setText("Category #{0}".format(int(self.number) + 1))
        self.custom_name_edit.setText(self.name)
        self.main_category__edit.setText(self.main_category)
        self.subcategory_edit.setText(self.subcategory)
        self.def_oper_type_edit.setCurrentText(self.def_oper_type)

        # Setting widgets to not enabled
        self.custom_name_edit.setEnabled(False)
        self.main_category__edit.setEnabled(False)
        self.subcategory_edit.setEnabled(False)
        self.def_oper_type_edit.setEnabled(False)

        # Setting button text
        self.primary_btn.setText("Edit")
        self.secondary_btn.setText("Delete")

    def edit_category(self):
        """
        Method used for changing state of widgets to enabled/disabled.
        Enabled - edit mode
        Disabled - vied mode
        """
        if self.active:
            self.custom_name_edit.setEnabled(False)
            self.main_category__edit.setEnabled(False)
            self.subcategory_edit.setEnabled(False)
            self.def_oper_type_edit.setEnabled(False)
            self.primary_btn.setText("Edit")

            self.active = False
        else:
            self.custom_name_edit.setEnabled(True)
            self.main_category__edit.setEnabled(True)
            self.subcategory_edit.setEnabled(True)
            self.def_oper_type_edit.setEnabled(True)
            self.primary_btn.setText("Save")

            self.active = True

    def delete_category(self):
        """
        Method used for deleting currently viewed category from databse
        """
        # Deletion confirmation box
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Delete category?\nThis will permamently delete category!",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            category = {
                "Name": self.custom_name_edit.text(),
                "1_Main Category": self.main_category__edit.text(),
                "2_Subcategory": self.subcategory_edit.text(),
                "3_Default Operation Type": self.def_oper_type_edit.currentText(),
            }

            self.send_category.emit(category, str(self.number), "Delete")
            self.destroy()
        else:
            self.show()

    def close_event(self):
        """
        Sending cataegory data to save if any widget was edited.
        """
        send_signal = False

        if self.custom_name_edit.text() != self.name:
            send_signal = True

        if self.main_category__edit.text() != self.main_category:
            send_signal = True

        if self.subcategory_edit.text() != self.subcategory:
            send_signal = True

        if self.def_oper_type_edit.currentText() != self.def_oper_type:
            send_signal = True

        if send_signal and not self.active:
            category = {
                "Name": self.custom_name_edit.text(),
                "1_Main Category": self.main_category__edit.text(),
                "2_Subcategory": self.subcategory_edit.text(),
                "3_Default Operation Type": self.def_oper_type_edit.currentText(),
            }

            self.send_category.emit(category, str(self.number), "Update")

        self.destroy()


class AddTransaction(QWidget):
    """
    AddTrasaction creates new window with option to add new transaction to user operations.
    """

    # Signals
    send_transaction = Signal(dict, str)

    def __init__(self, user_categories=None):
        super().__init__()

        # User data
        self.user_categories = user_categories
        # self.user_categories = sorted(user_categories)
        # print(self.user_categories)

        # Variables
        self.validator = QDoubleValidator(bottom=0, decimals=2)
        self.validator.setNotation(QDoubleValidator.StandardNotation)
        self.today = datetime.today()

        self.init_window()

    def init_window(self):
        """
        Initialize AddTrasanction window
        """
        main_layout = QGridLayout()
        self.setLayout(main_layout)
        self.setContentsMargins(15, 5, 15, 5)
        self.resize(QSize(550, 375))
        self.setFixedSize(QSize(455, 425))
        main_layout.setSpacing(10)

        # Title label
        self.title_label = QLabel(self)
        self.title_label.setText("New Transaction")
        self.title_label.setStyleSheet(
            "color: black; font-size: 16pt; padding:5px; font-weight:bold;"
        )
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Transaction name - label
        self.tr_name_label = QLabel(self)
        self.tr_name_label.setText("Transaction name")
        self.tr_name_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Transaction name - lineedit
        self.tr_name_edit = QLineEdit(self)

        # Date of operation - label
        self.tr_date_label = QLabel(self)
        self.tr_date_label.setText("Date of operation")
        self.tr_date_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Date of operation - lineedit
        self.tr_date_edit = QDateEdit(self)
        self.tr_date_edit.setCalendarPopup(True)
        self.tr_date_edit.setDisplayFormat("dd.MM.yyyy")
        self.tr_date_edit.setDate(
            QDate(self.today.year, self.today.month, self.today.day)
        )

        # Shop / Person - label
        self.tr_vendor_label = QLabel(self)
        self.tr_vendor_label.setText("Shop / Person")
        self.tr_vendor_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_vendor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Shop / Person - lineedit
        self.tr_vendor_edit = QLineEdit(self)

        # Type of operation - label
        self.tr_type_label = QLabel(self)
        self.tr_type_label.setText("Type of operation")
        self.tr_type_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Type of operation - combobox
        self.tr_type_edit = QComboBox(self)
        self.tr_type_edit.addItems(TRANSACTION_TYPES)

        # Category - label
        self.tr_category_label = QLabel(self)
        self.tr_category_label.setText("Category")
        self.tr_category_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_category_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Category - lineedit
        self.tr_category_edit = QComboBox(self)
        self.tr_category_edit.addItems(
            sorted([category.get("Name") for category in self.user_categories.values()])
        )
        # Adjusting width of pop-up list to length of longest text
        font_metrics = QFontMetrics(self.tr_category_edit.font())
        max_width = (
            max(
                font_metrics.horizontalAdvance(self.tr_category_edit.itemText(i))
                for i in range(self.tr_category_edit.count())
            )
            + 40
        )
        self.tr_category_edit.view().setMinimumWidth(max_width)
        self.tr_category_edit.currentIndexChanged.connect(self.on_category_change)

        # Amount - label
        self.tr_amount_label = QLabel(self)
        self.tr_amount_label.setText("Amount")
        self.tr_amount_label.setStyleSheet("color: black; font-size: 12pt;")
        self.tr_amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tr_amount_label.setContentsMargins(0, 0, 0, 20)

        # Shop / Person - lineedit
        self.tr_amount_edit = QLineEdit(self)
        self.tr_amount_edit.setValidator(self.validator)
        self.tr_amount_edit.setContentsMargins(0, 0, 0, 10)

        btn_layout = QHBoxLayout()

        # Add button
        self.primary_btn = QPushButton("Add")
        self.primary_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.primary_btn.setMinimumHeight(40)
        self.primary_btn.setMinimumWidth(130)
        self.primary_btn.clicked.connect(self.create_transaction)

        # Cancel button
        self.secondary_btn = QPushButton("Cancel")
        self.secondary_btn.setStyleSheet(
            "QPushButton {background-color: #ff0000; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #ff8080; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.secondary_btn.setMinimumHeight(40)
        self.secondary_btn.setMinimumWidth(130)
        self.secondary_btn.clicked.connect(self.destroy)

        btn_layout.addWidget(self.primary_btn, 0)
        btn_layout.addWidget(self.secondary_btn, 0)

        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #ff0000; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff0000;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#ff8080;}"
        )
        self.close_btn.setMinimumHeight(40)
        self.close_btn.setMinimumWidth(130)
        self.close_btn.clicked.connect(self.destroy)
        self.close_btn.setVisible(False)

        # Spacer for bottom
        self.spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_layout.addWidget(
            self.title_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter
        )

        main_layout.addWidget(self.tr_name_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_name_edit, 1, 1)

        main_layout.addWidget(self.tr_date_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_date_edit, 2, 1)

        main_layout.addWidget(self.tr_vendor_label, 3, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_vendor_edit, 3, 1)

        main_layout.addWidget(self.tr_category_label, 4, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_category_edit, 4, 1)

        main_layout.addWidget(self.tr_type_label, 5, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_type_edit, 5, 1)

        main_layout.addWidget(self.tr_amount_label, 6, 0, Qt.AlignmentFlag.AlignLeft)
        main_layout.addWidget(self.tr_amount_edit, 6, 1)

        main_layout.addLayout(btn_layout, 7, 0, 1, 2)
        main_layout.addWidget(self.close_btn, 8, 0, Qt.AlignmentFlag.AlignLeft)

        main_layout.addItem(self.spacer)

        main_layout.setColumnMinimumWidth(0, 225)

    def on_category_change(self):
        for category in self.user_categories.values():
            if category.get("Name") == self.tr_category_edit.currentText():
                print(category)
                print(category.get("3_Default Operation Type"))
                self.tr_type_edit.setCurrentText(
                    category.get("3_Default Operation Type")
                )

    def create_transaction(self):
        """
        Send transaction dict based on user choices to database
        """
        transaction = {
            "1_name": self.tr_name_edit.text(),
            "2_date": self.tr_date_edit.text(),
            "3_vendor": self.tr_vendor_edit.text(),
            "4_type": self.tr_type_edit.currentText(),
            "5_category": self.tr_category_edit.currentText(),
            "6_amount": self.tr_amount_edit.text(),
        }

        self.send_transaction.emit(transaction, self.tr_type_edit.currentText())

        self.destroy()


class EditTransaction(AddTransaction):
    """
    EditTransaction creates window with option to edit choosen transaction.

    EditTransaction inherites AddTransaction class
    """

    send_transaction = Signal(dict, str, str)

    def __init__(
        self, number, name, date, seller, type, category, amount, user_categories=None
    ):
        super().__init__(user_categories)

        # Transaction data
        self.number = number
        self.name = name
        self.date = date
        self.seller = seller
        self.type = type
        self.category = category
        self.amount = amount

        # Variables
        self.active = False
        self.date_qdate = QDate(
            int(self.date.split(".")[2]),
            int(self.date.split(".")[1]),
            int(self.date.split(".")[0]),
        )

        # Changing AddTransaction widgets
        self.primary_btn.clicked.disconnect()
        self.primary_btn.clicked.connect(self.edit_transaction)
        self.secondary_btn.clicked.connect(self.delete_transaction)
        self.close_btn.setVisible(True)
        self.close_btn.clicked.connect(self.close_event)
        self.setFixedSize(QSize(455, 455))

        self.fill_widgets()

    def fill_widgets(self):
        """
        Method used for filling widget with choosen operation
        """
        # Filling widgets
        self.title_label.setText("Transaction #{0}".format(int(self.number) + 1))
        self.tr_name_edit.setText(self.name)
        self.tr_date_edit.setDate(self.date_qdate)
        self.tr_vendor_edit.setText(self.seller)
        self.tr_type_edit.setCurrentText(self.type)
        self.tr_category_edit.setCurrentText(self.category)
        self.tr_amount_edit.setText(self.amount)

        # Disable widgets
        self.title_label.setEnabled(False)
        self.tr_name_edit.setEnabled(False)
        self.tr_date_edit.setEnabled(False)
        self.tr_vendor_edit.setEnabled(False)
        self.tr_type_edit.setEnabled(False)
        self.tr_category_edit.setEnabled(False)
        self.tr_amount_edit.setEnabled(False)

        # Setting button text
        self.primary_btn.setText("Edit")
        self.secondary_btn.setText("Delete")

    def edit_transaction(self):
        """
        Method used for changing state of widgets to enabled/disabled.
        Enabled - edit mode
        Disabled - vied mode
        """
        if self.active:
            self.tr_name_edit.setEnabled(False)
            self.tr_date_edit.setEnabled(False)
            self.tr_vendor_edit.setEnabled(False)
            self.tr_type_edit.setEnabled(False)
            self.tr_category_edit.setEnabled(False)
            self.tr_amount_edit.setEnabled(False)
            self.primary_btn.setText("Edit")

            self.active = False
        else:
            self.tr_name_edit.setEnabled(True)
            self.tr_date_edit.setEnabled(True)
            self.tr_vendor_edit.setEnabled(True)
            self.tr_type_edit.setEnabled(True)
            self.tr_category_edit.setEnabled(True)
            self.tr_amount_edit.setEnabled(True)
            self.primary_btn.setText("Save")

            self.active = True

    def delete_transaction(self):
        """
        Method used for deleting currently viewed transaction from databse
        """
        # Deletion confirmation box
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Delete transaction?\nThis will permamently delete transaction!",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            transaction = {
                str(self.number): {
                    "1_name": self.tr_name_edit.text(),
                    "2_date": self.tr_date_edit.text(),
                    "3_vendor": self.tr_vendor_edit.text(),
                    "4_type": self.tr_type_edit.currentText(),
                    "5_category": self.tr_category_edit.currentText(),
                    "6_amount": self.tr_amount_edit.text(),
                }
            }

            self.send_transaction.emit(transaction, self.type, "Delete")
            self.destroy()
        else:
            self.show()

    def close_event(self):
        """
        Sending transaction data to save if any widget was edited on close
        """
        send_signal = False

        if self.tr_name_edit.text() != self.name:
            send_signal = True

        if self.tr_date_edit.text() != self.date:
            send_signal = True

        if self.tr_vendor_edit.text() != self.seller:
            send_signal = True

        if self.tr_type_edit.currentText() != self.type:
            send_signal = True

        if self.tr_category_edit.currentText() != self.category:
            send_signal = True

        if self.tr_amount_edit.text() != self.amount:
            send_signal = True

        if send_signal and not self.active:
            transaction = {
                str(self.number): {
                    "1_name": self.tr_name_edit.text(),
                    "2_date": self.tr_date_edit.text(),
                    "3_vendor": self.tr_vendor_edit.text(),
                    "4_type": self.tr_type_edit.currentText(),
                    "5_category": self.tr_category_edit.currentText(),
                    "6_amount": self.tr_amount_edit.text(),
                }
            }

            self.send_transaction.emit(
                transaction, self.type, self.tr_type_edit.currentText()
            )

        self.destroy()
