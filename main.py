import os
import sys
import json
import pandas as pd
from datetime import datetime
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from platformdirs import user_data_dir

from finance_app import (
    SignInWindow,
    MainSection,
    CategoriesSection,
    HistorySection,
    UpcomingSection,
    AnalysisSection,
    AccountSettings,
    AppSettings,
    AddTransaction,
    ErrorBox,
    center_window,
)
from finance_app.config import *


class MainWindow(QMainWindow):
    """
    Main app window
    """

    def __init__(self):
        super().__init__()

        # User data
        self.user_settings_path = None
        self.user_settings = None
        self.settings_check = False
        self.user_categories = None
        self.user_categories_path = None
        self.user_transactions = None
        self.user_transactions_path = None
        self.user_upcomings = None
        self.user_upcomings_path = None

        self.check_user_settings()

    def init_window(self):
        """
        Initializes main window

        Window is displayed after sign in or user login (any user data exisits)
        """
        self.setWindowTitle(APP_NAME)
        center_window(self, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.central_widget = QWidget()
        self.main_layout = QHBoxLayout(self.central_widget)

        # Sidebar
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet("border-top: 0px; border-right: 1px solid #b5c0c9;")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setSpacing(10)

        # User Name box
        self.user_box_btn = QPushButton(
            "{0} ".format(self.user_settings.get("USER_NAME"))
        )
        self.user_box_btn.setStyleSheet(
            "QPushButton {font-size: 15pt; color:black; border-right: 0px;} "
            + "QPushButton::pressed {font-size: 14pt; color:black; border-right: 0px;}"
        )
        self.user_box_btn.setMinimumHeight(30)
        self.user_box_btn.setIcon(QIcon(DOWN_ICON))
        self.user_box_btn.setLayoutDirection(Qt.RightToLeft)
        self.user_box_btn.clicked.connect(self.show_dropdown_menu)
        self.create_user_menu()

        # Add transaction
        self.add_transaction_btn = QPushButton(QIcon(ADD_ICON), "Add transaction")
        self.add_transaction_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.add_transaction_btn.setMinimumHeight(40)
        self.add_transaction_btn.setMinimumWidth(135)
        self.add_transaction_btn.clicked.connect(self.add_transaction)

        # Main section
        self.main_section_btn = QPushButton("Main")
        self.main_section_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#0085FC;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#4dacff;}"
        )
        self.main_section_btn.setMinimumHeight(35)
        self.main_section_btn.clicked.connect(
            lambda: self.stacked_categories.setCurrentIndex(0)
        )

        # Analysis section
        self.analysis_section_btn = QPushButton("Analysis")
        self.analysis_section_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#0085FC;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#4dacff;}"
        )
        self.analysis_section_btn.setMinimumHeight(35)
        self.analysis_section_btn.clicked.connect(
            lambda: self.stacked_categories.setCurrentIndex(2)
        )
        # History section
        self.history_section_btn = QPushButton("History")
        self.history_section_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#0085FC;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#4dacff;}"
        )
        self.history_section_btn.setMinimumHeight(35)
        self.history_section_btn.clicked.connect(
            lambda: self.stacked_categories.setCurrentIndex(3)
        )

        # Upcoming section
        self.upcoming_section_btn = QPushButton("Upcoming")
        self.upcoming_section_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#0085FC;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#4dacff;}"
        )
        self.upcoming_section_btn.setMinimumHeight(35)
        self.upcoming_section_btn.clicked.connect(
            lambda: self.stacked_categories.setCurrentIndex(4)
        )

        # Categories section
        self.categories_section_btn = QPushButton("Categories")
        self.categories_section_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #566876; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#566876;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #899ba9; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#899ba9;}"
        )
        self.categories_section_btn.setMinimumHeight(35)
        self.categories_section_btn.clicked.connect(
            lambda: self.stacked_categories.setCurrentIndex(1)
        )

        # Creating app sections
        self.main_section = MainSection(
            user_settings=self.user_settings,
            user_transactions=self.user_transactions,
            user_transactions_path=self.user_transactions_path,
            user_upcomings=self.user_upcomings,
            user_upcomings_path=self.user_upcomings_path,
        )
        self.categories_section = CategoriesSection(
            user_categories=self.user_categories,
            user_categories_path=self.user_categories_path,
        )
        self.categories_section.update_category.connect(self.get_category)

        self.history_section = HistorySection(
            current_acc_balance=self.user_settings.get("CURRENT_ACCOUNT_BALANCE"),
            currency=self.user_settings.get("CURRENCY"),
            user_transactions=self.user_transactions,
            user_transactions_path=self.user_transactions_path,
            user_categories=self.user_categories,
        )
        self.history_section.update_transaction.connect(self.get_transaction)

        self.upcoming_section = UpcomingSection(
            current_acc_balance=self.user_settings.get("CURRENT_ACCOUNT_BALANCE"),
            currency=self.user_settings.get("CURRENCY"),
            user_upcomings=self.user_upcomings,
            user_upcomings_path=self.user_upcomings_path,
            user_categories=self.user_categories,
        )
        self.upcoming_section.update_transaction.connect(self.get_transaction)

        self.analysis_section = AnalysisSection(
            user_settings=self.user_settings,
            user_transactions=self.user_transactions,
            user_transactions_path=self.user_transactions_path,
            user_upcomings=self.user_upcomings,
            user_upcomings_path=self.user_upcomings_path,
            user_categories=self.user_categories,
        )

        # Stacked widgest for sections
        self.stacked_categories = QStackedWidget()
        self.stacked_categories.addWidget(self.main_section)
        self.stacked_categories.addWidget(self.categories_section)
        self.stacked_categories.addWidget(self.analysis_section)
        self.stacked_categories.addWidget(self.history_section)
        self.stacked_categories.addWidget(self.upcoming_section)
        self.stacked_categories.setCurrentIndex(
            SECTION_LIST.get(self.user_settings.get("DEFAULT_VIEW"))
        )

        # Adding widgets to layout
        self.sidebar_layout.addWidget(
            self.user_box_btn, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.sidebar_layout.addWidget(self.add_transaction_btn)
        self.sidebar_layout.addWidget(self.main_section_btn)
        self.sidebar_layout.addWidget(self.analysis_section_btn)
        self.sidebar_layout.addWidget(self.history_section_btn)
        self.sidebar_layout.addWidget(self.upcoming_section_btn)
        self.sidebar_layout.addWidget(self.categories_section_btn)
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.stacked_categories)

        # Setting central widget
        self.setCentralWidget(self.central_widget)
        self.sidebar_layout.addStretch(1)

    def create_user_menu(self):
        """
        Creation of user menu which is dropdown box with:
            - Account settings
            - App settings
        """
        self.user_menu = QMenu(self)
        self.user_menu.setObjectName("DropDownMenu")
        self.user_menu.setStyleSheet(
            "#DropDownMenu {border: 2px solid #b5c0c9; border-radius:10px;}"
        )

        # Widget for holding buttons
        menu_widget = QWidget(self)
        layout = QVBoxLayout(menu_widget)

        # Account settings buttons
        self.acc_settings_btn = QPushButton("Account Settings")
        self.acc_settings_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #566876; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#566876;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #899ba9; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#899ba9;}"
        )
        self.acc_settings_btn.setMinimumHeight(30)
        self.acc_settings_btn.setMinimumWidth(125)

        self.acc_settings_btn.clicked.connect(self.show_account_settings)

        # App settings button
        self.app_settings_btn = QPushButton("App Settings")
        self.app_settings_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #566876; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#566876;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #899ba9; border-width: 2px; border-radius: 10px; font-size: 10pt; color:#899ba9;}"
        )
        self.app_settings_btn.setMinimumHeight(30)
        self.app_settings_btn.setMinimumWidth(125)
        self.app_settings_btn.clicked.connect(self.show_app_settings)

        # Add buttons to the layout
        layout.addWidget(self.acc_settings_btn)
        layout.addWidget(self.app_settings_btn)

        # Create a QWidgetAction to add custom widgets to the QMenu
        widget_action = QWidgetAction(self)
        widget_action.setDefaultWidget(menu_widget)

        # Add the QWidgetAction to the dropdown menu
        self.user_menu.addAction(widget_action)

    def show_dropdown_menu(self):
        """
        Method to show dropdown user menu
        """
        # Show the dropdown menu under the main button
        self.user_menu.exec(
            self.user_box_btn.mapToGlobal(self.user_box_btn.rect().bottomLeft())
        )

    def check_user_settings(self, reload=False):
        """
        Checking if user settings are present
        """
        # Get the user data directory for the application
        settings_dir = user_data_dir(APP_NAME, VERSION)

        print(settings_dir)

        # Create the settings directory if it doesn't exist
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)

        # Define the path to the user-specific settings file
        self.user_settings_path = os.path.join(settings_dir, "user_settings.json")

        if os.path.exists(self.user_settings_path):
            with open(self.user_settings_path, "r") as file:
                self.user_settings = json.load(file)
                self.settings_check = True

            if not reload:
                self.load_user_profile()

                self.init_window()

                if not self.user_transactions is None:
                    self.update_acc_bal()
        else:
            self.sign_in()

    def load_user_profile(self):
        """
        Loading user data stored in user choosen folder
        """
        user_folder = self.user_settings.get("USER_FOLDER")

        # User categories
        self.user_categories_path = os.path.join(user_folder, USER_CATEGORIES)
        if os.path.exists(self.user_categories_path):
            with open(self.user_categories_path, "r") as file:
                self.user_categories = json.load(file)

        # User transactions
        self.user_transactions_path = os.path.join(user_folder, USER_TRANSACTIONS)
        if os.path.exists(self.user_transactions_path):
            with open(self.user_transactions_path, "r") as file:
                self.user_transactions = json.load(file)

        # User upcoming operations
        self.user_upcomings_path = os.path.join(user_folder, USER_UPCOMING_OPER)
        if os.path.exists(self.user_upcomings_path):
            with open(self.user_upcomings_path, "r") as file:
                self.user_upcomings = json.load(file)

    def sign_in(self):
        """
        Show sign in window
        """
        self.sign_in_window = SignInWindow(self.user_settings, self.user_settings_path)
        self.sign_in_window.signed_in_signal.connect(self.signed_in_check)
        self.setCentralWidget(self.sign_in_window)
        center_window(self, 500, 475)

    @Slot(bool)
    def signed_in_check(self, signed):
        """
        Get signed in signal from SignInWindow and login user

        Args:
            signed (bool): signal from SignInWindow
        """
        if signed:
            self.check_user_settings()

    def add_transaction(self):
        """
        Method user for displaying window to add transaction

        After filling all necessary information and closing window new transaction will be passed to get_transaction method.

        If user has no added categories error will be shown and then new category window will be shown.

        """
        if self.user_categories is None or len(self.user_categories) == 0:
            msg = "Please create at least one category before adding transaction!"
            ErrorBox(self, title="No categories!", msg=msg)
            self.stacked_categories.setCurrentIndex(1)
            self.categories_section.add_category()
        else:
            # self.add_transaction_window = AddTransaction(
            #     [category.get("Name") for category in self.user_categories.values()]
            # )
            self.add_transaction_window = AddTransaction(
                user_categories=self.user_categories
            )
            self.add_transaction_window.show()

            self.add_transaction_window.send_transaction.connect(self.get_transaction)

    @Slot(dict, str)
    def get_transaction(self, transaction, type):
        """
        Method used for transaction data manipulation and database updating.
        During update all needed databases, tables and charts are updated with new information.

        Args:
            transaction (dict): information abaout transaction provided by the user
            type (str): type of operation:
                - Upcoming - user created transaction which is planned
                - Delete - delete choosen transaction
                - Update - update transaction based on choosen information. It can be:
                    - Updated to upcoming - transaction changes it type to upcoming operation
                    - Updated to transaction - transaction changes it type to operation resolved
                - New transaction - adding new transaction to database
        """
        oper_type = type.split("-")[0]
        match oper_type:
            case "Upcoming":
                if self.user_upcomings is None:
                    self.user_upcomings = {"0": transaction}
                else:
                    self.user_upcomings.update(
                        {str(len(self.user_upcomings.keys())): transaction}
                    )

                # Update file
                with open(self.user_upcomings_path, "w") as file:
                    json.dump(self.user_upcomings, file)

                # Update information in sections
                self.main_section.update_operations(self.user_upcomings, type)
                self.analysis_section.update_operations(self.user_upcomings, type)
                self.upcoming_section.update_upcoming_oper(self.user_upcomings)
            case "Delete":
                match type.split("-")[1]:
                    case "Upcoming":
                        # Delete upcoming transaction
                        for key in transaction.keys():
                            self.user_upcomings.pop(key)
                        # self.user_upcomings.pop(list(transaction.keys())[0])

                        # Update upcomings dict keys
                        new_key = 0

                        temp_list = list(self.user_upcomings.items())
                        self.user_upcomings.clear()
                        for key, value in temp_list:
                            self.user_upcomings[str(new_key)] = value
                            new_key += 1

                        # Update file
                        with open(self.user_upcomings_path, "w") as file:
                            json.dump(self.user_upcomings, file)

                        # Update information in sections
                        self.main_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.analysis_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )

                        self.upcoming_section.update_upcoming_oper(self.user_upcomings)

                    case _:
                        # Delete transaction from expense/income
                        for key in transaction.keys():
                            self.user_transactions.pop(key)

                        # Update expense/income dict keys
                        new_key = 0

                        temp_list = list(self.user_transactions.items())
                        self.user_transactions.clear()
                        for key, value in temp_list:
                            self.user_transactions[str(new_key)] = value
                            new_key += 1

                        # Save file
                        with open(self.user_transactions_path, "w") as file:
                            json.dump(self.user_transactions, file)

                        self.main_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.history_section.update_operations(self.user_transactions)
                        self.update_acc_bal()

            case "Update":
                match type.split("-")[1]:
                    case "Upcoming":
                        self.user_upcomings.update(transaction)

                        # Update file
                        with open(self.user_upcomings_path, "w") as file:
                            json.dump(self.user_upcomings, file)

                        # Update information in sections
                        self.main_section.update_operations(self.user_upcomings, type)
                        self.analysis_section.update_operations(
                            self.user_upcomings, type
                        )
                        self.upcoming_section.update_upcoming_oper(self.user_upcomings)

                    case "Transaction":
                        self.user_transactions.update(transaction)

                        # Update file
                        with open(self.user_transactions_path, "w") as file:
                            json.dump(self.user_transactions, file)

                        # Update information in sections
                        self.main_section.update_operations(
                            self.user_transactions, type
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, type
                        )
                        self.history_section.update_operations(self.user_transactions)
                        self.update_acc_bal()
                    case "UpcomingtoTransaction":
                        # Delete upcoming transaction
                        self.user_upcomings.pop(list(transaction.keys())[0])

                        # Add transaction to the end of expense/income list
                        self.user_transactions.update(
                            {
                                str(
                                    len(self.user_transactions.keys())
                                ): transaction.get(list(transaction.keys())[0])
                            }
                        )

                        # Update upcomings dict keys
                        new_key = 0

                        temp_list = list(self.user_upcomings.items())
                        self.user_upcomings.clear()
                        for key, value in temp_list:
                            self.user_upcomings[str(new_key)] = value
                            new_key += 1

                        # Update files
                        with open(self.user_upcomings_path, "w") as file:
                            json.dump(self.user_upcomings, file)

                        with open(self.user_transactions_path, "w") as file:
                            json.dump(self.user_transactions, file)

                        # Update information in sections
                        self.main_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.main_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.analysis_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.upcoming_section.update_upcoming_oper(self.user_upcomings)
                        self.history_section.update_operations(self.user_transactions)
                        self.update_acc_bal()

                    case "TransactiontoUpcoming":
                        # Delete transaction from expense/income
                        self.user_transactions.pop(list(transaction.keys())[0])

                        # Add transaction to the end of upcoming list
                        self.user_upcomings.update(
                            {
                                str(len(self.user_upcomings.keys())): transaction.get(
                                    list(transaction.keys())[0]
                                )
                            }
                        )

                        # Update expense/income dict keys
                        new_key = 0

                        temp_list = list(self.user_transactions.items())
                        self.user_transactions.clear()
                        for key, value in temp_list:
                            self.user_transactions[str(new_key)] = value
                            new_key += 1

                        # Update files
                        with open(self.user_upcomings_path, "w") as file:
                            json.dump(self.user_upcomings, file)

                        with open(self.user_transactions_path, "w") as file:
                            json.dump(self.user_transactions, file)

                        # Update information in sections
                        self.main_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.main_section.update_operations(
                            self.user_transactions, "Transaction"
                        )

                        self.analysis_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, "Transaction"
                        )

                        self.upcoming_section.update_upcoming_oper(self.user_upcomings)
                        self.history_section.update_operations(self.user_transactions)
                        self.update_acc_bal()

            case _:
                if self.user_transactions is None:
                    self.user_transactions = {"0": transaction}
                else:
                    self.user_transactions.update(
                        {str(len(self.user_transactions.keys())): transaction}
                    )

                # Update files
                with open(self.user_transactions_path, "w") as file:
                    json.dump(self.user_transactions, file)

                # Update information in sections
                self.main_section.update_operations(self.user_transactions, type)
                self.analysis_section.update_operations(self.user_transactions, type)
                self.history_section.update_operations(self.user_transactions)
                self.update_acc_bal()

        # Update analysis if auto run is set to True
        if self.user_settings.get("ANALYSIS_AUTO_RUN") == 1:
            self.analysis_section.update_analysis()

    @Slot(dict, str, str)
    def get_category(self, category, number, activity):
        """
        Method used for catching operation made on operation categories.

        Args:
            category (dict): Category dict with all informations provided by the user
            number (str): number of category in database
            activity (str): origin of activity made by the user. It can be:
                - Update - update category data
                - Delete - delete choosen category
        """
        match activity:
            case "Update":
                # Get name of old category
                old_cat_name = self.user_categories[number].get("Name")
                new_cat_name = category.get("Name")

                # Update category on specific index
                self.user_categories[number] = category

                # Update categories dict in sections
                self.history_section.user_categories = self.user_categories
                self.upcoming_section.user_categories = self.user_categories
                self.analysis_section.update_categories(self.user_categories)
                self.categories_section.update_categories(self.user_categories)

                # Update categories file
                with open(self.user_categories_path, "w") as file:
                    json.dump(self.user_categories, file)

                # Update categories names (if changed) in transaction/upcomings
                if new_cat_name != old_cat_name:
                    # Update transactions
                    if not self.user_transactions is None:
                        for key, value in self.user_transactions.items():
                            if value.get("5_category") == old_cat_name:
                                value["5_category"] = new_cat_name
                                self.user_transactions[key] = value

                        with open(self.user_transactions_path, "w") as file:
                            json.dump(self.user_transactions, file)

                        self.main_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.history_section.update_operations(self.user_transactions)

                    if not self.user_upcomings is None:
                        # Update upcomings
                        for key, value in self.user_upcomings.items():
                            if value.get("5_category") == old_cat_name:
                                value["5_category"] = new_cat_name
                                self.user_upcomings[key] = value

                        with open(self.user_upcomings_path, "w") as file:
                            json.dump(self.user_upcomings, file)

                        self.main_section.update_operations(
                            self.user_upcomings, "Upcoming"
                        )
                        self.analysis_section.update_operations(
                            self.user_transactions, "Transaction"
                        )
                        self.upcoming_section.update_upcoming_oper(self.user_upcomings)

            case "Delete":
                # Delete upcoming transaction
                self.user_categories.pop(number)

                # Update upcomings dict keys
                new_key = 0

                temp_list = list(self.user_categories.items())
                self.user_categories.clear()
                for key, value in temp_list:
                    self.user_categories[str(new_key)] = value
                    new_key += 1

                # Update categories dict in sections
                self.history_section.user_categories = self.user_categories
                self.upcoming_section.user_categories = self.user_categories
                self.analysis_section.user_categories = self.user_categories
                self.analysis_section.update_categories(self.user_categories)
                self.categories_section.update_categories(self.user_categories)

                # Update categories file
                with open(self.user_categories_path, "w") as file:
                    json.dump(self.user_categories, file)
            case _:  # New category
                if self.user_categories is None:
                    self.user_categories = {"0": category}
                else:
                    self.user_categories.update(
                        {str(len(self.user_categories.keys())): category}
                    )

                with open(self.user_categories_path, "w") as file:
                    json.dump(self.user_categories, file)

                # Update information in sections
                self.history_section.user_categories = self.user_categories
                self.upcoming_section.user_categories = self.user_categories
                self.analysis_section.user_categories = self.user_categories
                self.analysis_section.update_categories(self.user_categories)
                self.categories_section.update_categories(self.user_categories)

    def update_acc_bal(self):
        """
        Current account balance update and Text widgets displaying this value in every section.
        """
        last_transaction = datetime.today().strftime("%d-%m-%Y")
        curr_acc_bal = self.user_settings.get("CURRENT_ACCOUNT_BALANCE")

        if not self.user_transactions is None and len(self.user_transactions) > 0:
            # Data prep
            temp_transactions = pd.DataFrame(self.user_transactions).T.reset_index(
                drop=True
            )
            temp_transactions["6_amount"] = temp_transactions["6_amount"].apply(
                lambda x: float(x.replace(" ", "").replace(",", "."))
            )

            # Last transaction date
            last_transaction = temp_transactions["2_date"].iloc[-1]

            # Calculate current account balance
            transaction_summary = temp_transactions.groupby(["4_type"])[
                "6_amount"
            ].sum()
            income = (
                0
                if "Income" not in transaction_summary.index.values
                else transaction_summary.loc["Income"]
            )
            expense = (
                0
                if "Expense" not in transaction_summary.index.values
                else transaction_summary.loc["Expense"]
            )
            curr_acc_bal = round(
                self.user_settings.get("CURRENT_ACCOUNT_BALANCE") + (income - expense),
                2,
            )

        # Update every text widget containing current account balance
        self.main_section.curr_acc_label.setText(
            "Hello {0}!\n\nYour account balance\nas of {1} is\n{2} {3}".format(
                self.user_settings.get("USER_NAME"),
                last_transaction.replace(".", "-"),
                str(curr_acc_bal).replace(".", ","),
                self.user_settings.get("CURRENCY"),
            )
        )

        for section in [self.history_section, self.upcoming_section]:
            section.curr_acc_label.setText(
                "Account balance as of {0}: {1} {2}".format(
                    last_transaction.replace(".", "-"),
                    str(curr_acc_bal).replace(".", ","),
                    self.user_settings.get("CURRENCY"),
                )
            )

    def show_account_settings(self):
        """
        Method used for showing window with user accunt settings.
        """
        self.account_settings_window = AccountSettings(
            self,
            user_settings=self.user_settings,
            user_settings_path=self.user_settings_path,
        )
        self.account_settings_window.show()

        self.account_settings_window.update_settings.connect(
            lambda: self.check_user_settings(reload=True)
        )

        # self.account_settings_window.account_deletion.connect(self.destroy)

    def show_app_settings(self):
        """
        Method used for showing window with user accunt settings.
        """
        self.app_settings_window = AppSettings(
            self,
            user_settings=self.user_settings,
            user_settings_path=self.user_settings_path,
        )
        self.app_settings_window.show()

        self.app_settings_window.update_settings.connect(
            lambda: self.check_user_settings(reload=True)
        )

    def set_dark_theme(self, app):
        """
        Setting dark app theme
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        app.setPalette(palette)

    def set_white_theme(self, app):
        """
        Setting white app theme
        """
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.AlternateBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.Button, QColor(150, 150, 150))
        palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(191, 191, 191))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        palette.setColor(QPalette.PlaceholderText, QColor(166, 166, 166))
        app.setPalette(palette)
        app.setStyleSheet(
            """
            /*QLINEDIT STYLE
            QLineEdit{
                background-color: white; 
                border-style: solid; 
                border-color: #bfbfbf; 
                border-width: 2px; 
                border-radius: 10px; 
                padding: 6px;
            }*/
            /* COMBOBOX STYLE*/
            QComboBox, QLineEdit, QDateEdit{
                background-color: white; 
                border-style: solid; 
                border-color: #bfbfbf; 
                border-width: 2px; 
                border-radius: 10px; 
                padding: 6px; 
                combobox-popup: 0;
            }
            /* LIST OF POSITIONS STYLE */
            QComboBox QAbstractItemView {
                background-color: white; 
                color: black;
                border: 2px solid #bfbfbf;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item{
                border-radius: 5px;
            }
            QComboBox QAbstractItemView::item:hover{
                background-color: #bfbfbf;
            }
            /* SCROLLBAR STYLE*/
            QScrollBar:vertical{
                border: 0px solid white;
                background-color: white; 
                margin: 15px 0px 15px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                border: 1px solid #bfbfbf;
            }

            /* SCROLLBAR TOP BUTTON STYLE */
            QScrollBar::sub-line:vertical {
                border: 1px solid #bfbfbf;
                height:15px;
                border-top-right-radius: 5px; 
                subcontrol-position: top;
                subcontrol-origin: margin;
                image: url(images:up_icon.png)
            }

            /* SCROLLBAR BOTTOM BUTTON STYLE */
            QScrollBar::add-line:vertical {
                border: 1px solid #bfbfbf;
                border-bottom-right-radius: 5px; 
                height:15px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                image: url(images:down_icon.png)
            }

            /* SCROLLBAR ELEMENT STATE STYLE */
            QScrollBar::sub-line:hover, QScrollBar::add-line:hover, QScrollBar::handle:hover {
                background: #b3b3b3;
            }

            QScrollBar::sub-line:pressed,QScrollBar::add-line:pressed, QScrollBar::handle:pressed {
                background: #999999;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
                background: none; 
            }

            /* QCOMBOBOX DROP - DOWN BUTTON STYLE */
            QComboBox::drop-down:button, QDateEdit::drop-down{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                background:#e6e6e6;
                border-top-right-radius: 8px; 
                border-bottom-right-radius: 8px; 
            }
            QComboBox::down-arrow:button, QDateEdit::down-arrow{
                image: url(images:down_icon.png)
                }
            QToolTip {
                background: white;
                color: black;
                padding: 2px;
                font-size: 10pt;
            }

            QCheckBox::indicator{
                width: 20px; 
                height: 20px;
            }
            """
        )


def main():
    """
    App initialization
    """
    # Locale
    QLocale.setDefault(QLocale(QLocale.Polish, QLocale.Poland))

    # Path for Qt search
    QDir.addSearchPath(
        "images",
        IMAGES_DIR,
    )

    # App object
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))

    # App main window
    window = MainWindow()
    window.set_white_theme(app)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
