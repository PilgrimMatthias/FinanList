from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta

import json

from finance_app.widgets.table_widget import TableWidget
from finance_app.config import *
from finance_app.widgets.bar_plot_widget import BarChart


class MainSection(QWidget):
    """
    Main section of the app where basic info is shown, such as:
        - Last 30 operations
        - 30 planned operations
        - Current account balance
        - Cashflow from last 3 months
    """

    def __init__(
        self,
        user_settings,
        user_transactions,
        user_transactions_path,
        user_upcomings,
        user_upcomings_path,
    ) -> None:
        super().__init__()

        # User data
        self.user_settings = user_settings
        self.user_transactions = user_transactions
        self.user_transactions_path = user_transactions_path
        self.user_upcomings = user_upcomings
        self.user_upcomings_path = user_upcomings_path

        self.user_upcomings_df = pd.DataFrame(self.user_upcomings).T.reset_index(
            drop=True
        )
        self.user_upcomings_df = self.user_upcomings_df[
            [
                col
                for col in self.user_upcomings_df.columns
                if not "vendor" in col and not "type" in col
            ]
        ]

        # User information
        self.user_name = self.user_settings.get("USER_NAME")
        self.current_acc_balance = self.user_settings.get("CURRENT_ACCOUNT_BALANCE")
        self.monthly_gross_salary = self.user_settings.get("MONTHLY_GROSS_SALARY")
        self.monthly_net_salary = self.user_settings.get("MONTHLY_NET_SALARY")
        self.avg_monthly_expense = self.user_settings.get("AVERAGE_MONTHLY_EXPENSE")
        self.currency = self.user_settings.get("CURRENCY")
        self.data_path = self.user_settings.get("USER_FOLDER")

        self.recent_oper_num = (
            7
            if self.user_transactions is None
            else (
                len(self.user_transactions.keys())
                if len(self.user_transactions.keys()) < 30
                else 30
            )
        )
        self.upcoming_oper_num = (
            7
            if self.user_upcomings is None
            else (
                len(self.user_upcomings.keys())
                if len(self.user_upcomings.keys()) < 30
                else 30
            )
        )

        self.plot_check = False

        self.init_section()

    def init_section(self):
        """
        Initialize section
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(15)

        # Title layout
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(15)
        self.summary_layout.setContentsMargins(0, 0, 0, 0)

        # Curent account balance
        self.curr_acc_label = QLabel(self)
        self.curr_acc_label.setText(
            "Hello {0}! Your account balance as of\n{1}\nuequels:{2} {3}".format(
                self.user_name,
                datetime.today().strftime("%d-%m-%Y"),
                str(self.current_acc_balance).replace(".", ","),
                self.currency,
            )
        )
        self.curr_acc_label.setContentsMargins(0, 0, 0, 0)
        self.curr_acc_label.setStyleSheet(
            "color: black; font-size: 20pt; border: 1px solid #b5c0c9; border-radius:10px; padding:20px;"
        )
        self.curr_acc_label.setWordWrap(True)
        self.curr_acc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.summary_layout.addWidget(
            self.curr_acc_label, 0  # , alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.calculate_plot_data()

        # Table layout
        table_layout = QHBoxLayout()
        table_layout.setSpacing(15)

        self.rec_oper_frame = QFrame()
        self.rec_oper_frame.setStyleSheet(
            "border: 1px solid #b5c0c9; border-radius:10px;"
        )
        self.rec_oper_layout = QVBoxLayout(self.rec_oper_frame)
        self.rec_oper_layout.setContentsMargins(0, 0, 0, 0)

        # Tytuł tabeli
        self.recent_oper_label = QLabel(self)
        self.recent_oper_label.setText("Recent operations")
        self.recent_oper_label.setContentsMargins(0, 7, 0, 3)
        self.recent_oper_label.setStyleSheet(
            "color: black; font-size: 18pt; border:0px;"
        )

        self.recent_oper_table = TableWidget(
            parent=self,
            row_num=self.recent_oper_num,
            col_num=len(RECENT_OPERATIONS_HEADERS),
            header_names=RECENT_OPERATIONS_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            data=pd.DataFrame(self.user_transactions)
            .T.reset_index(drop=True)
            .sort_index(ascending=False)
            .reset_index(drop=True)
            .iloc[: self.recent_oper_num],
            editable=False,
        )

        self.rec_oper_layout.addWidget(
            self.recent_oper_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.rec_oper_layout.addWidget(self.recent_oper_table)

        self.plan_oper_frame = QFrame()
        self.plan_oper_frame.setStyleSheet(
            "border: 1px solid #b5c0c9; border-radius:10px;"
        )
        self.plan_oper_layout = QVBoxLayout(self.plan_oper_frame)
        self.plan_oper_layout.setContentsMargins(0, 0, 0, 0)

        # Table title
        self.planned_oper_label = QLabel(self)
        self.planned_oper_label.setText("Planned operations")
        self.planned_oper_label.setContentsMargins(0, 7, 0, 3)
        self.planned_oper_label.setStyleSheet(
            "color: black; font-size: 18pt; border:0px;"
        )

        # Planned operations table
        self.planned_oper_table = TableWidget(
            parent=self,
            row_num=self.upcoming_oper_num,
            col_num=len(PLANNED_OPERATIONS_HEADERS),
            header_names=PLANNED_OPERATIONS_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            data=self.user_upcomings_df.iloc[: self.upcoming_oper_num],
            editable=False,
        )

        self.plan_oper_layout.addWidget(
            self.planned_oper_label, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.plan_oper_layout.addWidget(self.planned_oper_table)

        table_layout.addWidget(self.rec_oper_frame, 2)
        table_layout.addWidget(self.plan_oper_frame, 1)

        # Spacer for bottom
        main_layout.addLayout(self.summary_layout, 1)
        main_layout.addLayout(table_layout, 2)

    def update_operations(self, data, type):
        """
        Update data in table and on on the plot


        Args:
            data (dict): transaction
            type (str): type of operations
        """
        data = (
            pd.DataFrame(data)
            .T.reset_index(drop=True)
            .sort_index(ascending=False)
            .reset_index(drop=True)
        )

        match type:
            case "Upcoming":
                data = data = data[
                    [
                        col
                        for col in data.columns
                        if not "vendor" in col and not "type" in col
                    ]
                ]
                self.planned_oper_table.clear_table()
                self.planned_oper_table.update_table(
                    data.iloc[:7],
                )
            case _:
                self.recent_oper_table.clear_table()
                self.recent_oper_table.update_table(
                    data.iloc[:30],
                )

        self.calculate_plot_data()

    def calculate_plot_data(self):
        """
        Method for calculating data for plot and then displaying it on the screen
        """
        # Columns to get from databases
        columns_to_get = ["1_name", "2_date", "4_type", "5_category", "6_amount"]

        # Prepare transactions database
        transactions = (
            pd.DataFrame(self.user_transactions)
            .T.reset_index(drop=True)
            .copy()[columns_to_get]
        )

        transactions["2_date"] = transactions["2_date"].apply(
            lambda x: datetime.strptime(x, "%d.%m.%Y")
        )
        transactions["6_amount"] = transactions["6_amount"].apply(
            lambda x: float(x.replace(",", ".").replace(" ", ""))
        )

        transactions["Year-month"] = transactions["2_date"].apply(
            lambda x: x.strftime("%Y-%m")
        )

        transactions = (
            transactions.groupby(["Year-month", "4_type"])["6_amount"]
            .sum()
            .reset_index(drop=False)
        )

        # Prepare expenses
        expense = transactions[transactions["4_type"] == "Expense"].drop(
            "4_type", axis=1
        )
        expense.columns = ["Year-month", "Expense"]

        # Prepare Income
        income = transactions[transactions["4_type"] == "Income"].drop("4_type", axis=1)
        income.columns = ["Year-month", "Income"]

        # Prepare result table
        result_table = transactions["Year-month"].drop_duplicates()
        result_table = pd.merge(
            left=result_table, right=income, how="left", on="Year-month"
        )
        result_table = pd.merge(
            left=result_table, right=expense, how="left", on="Year-month"
        ).fillna(0)

        result_table.index = result_table["Year-month"]
        result_table = result_table.iloc[-3:].drop("Year-month", axis=1)

        # Deleting plot widget
        if self.plot_check:
            self.plot_frame.deleteLater()
            self.plot_frame_layout.deleteLater()
            self.aggregate_plot.deleteLater()

        # Creating new chart
        self.aggregate_plot = BarChart(
            parent=self,
            data=result_table,
            title="Monthly cashflow - last 3 months",
            legend=False,
            x_label=None,
            y_label="[{0}]".format(self.currency),
            y_axis_visible=False,
            gridlines=False,
        )

        # Frame for chart
        self.plot_frame = QFrame()
        self.plot_frame.setStyleSheet("border: 1px solid #b5c0c9; border-radius:10px;")
        self.plot_frame_layout = QVBoxLayout(self.plot_frame)
        self.plot_frame_layout.setContentsMargins(0, 0, 0, 0)
        self.plot_frame_layout.setSpacing(5)
        self.plot_frame_layout.addWidget(self.aggregate_plot, 0)

        # Adding chart in frame to main layout
        self.summary_layout.addWidget(self.plot_frame, 1)

        self.plot_check = True  # Plot present on screen
