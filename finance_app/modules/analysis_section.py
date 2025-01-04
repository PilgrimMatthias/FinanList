from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import pandas as pd

from datetime import datetime
from dateutil.relativedelta import relativedelta

import json

from finance_app.widgets.table_widget import TableWidget
from finance_app.widgets.bar_plot_widget import BarChart
from finance_app.config import *
from finance_app.modules.analysis_calculation import Analysis
from finance_app.modules.status_windows import ErrorBox


class AnalysisSection(QWidget):
    """
    Analysis sections is section were user can analsise past and future operations.
    Currently user can:
        - Analyse categories
        - Analyse monthly cashflow
        - Make prognosis for future months
    """

    def __init__(
        self,
        user_settings,
        user_transactions,
        user_transactions_path,
        user_upcomings,
        user_upcomings_path,
        user_categories,
    ) -> None:
        super().__init__()

        # User data
        self.user_settings = user_settings
        self.user_transactions = user_transactions
        self.user_transactions_path = user_transactions_path
        self.user_upcomings = user_upcomings
        self.user_upcomings_path = user_upcomings_path
        self.user_categories = user_categories

        # User account info
        self.user_name = self.user_settings.get("USER_NAME")
        self.current_acc_balance = self.user_settings.get("CURRENT_ACCOUNT_BALANCE")
        self.monthly_gross_salary = self.user_settings.get("MONTHLY_GROSS_SALARY")
        self.monthly_net_salary = self.user_settings.get("MONTHLY_NET_SALARY")
        self.avg_monthly_expense = self.user_settings.get("AVERAGE_MONTHLY_EXPENSE")
        self.currency = self.user_settings.get("CURRENCY")
        self.data_path = self.user_settings.get("USER_FOLDER")
        self.user_def_analysis = self.user_settings.get("DEFAULT_ANALYSIS")

        self.last_operation_date = datetime.today().strftime("%d.%m.%Y")
        if not self.user_transactions is None and len(self.user_transactions) > 0:
            self.last_operation_date = self.user_transactions.get(
                list(self.user_transactions.keys())[-1]
            ).get("2_date")

        self.prognosis_date_to = (
            datetime.strptime(self.last_operation_date, "%d.%m.%Y")
            + relativedelta(months=24)
        ).strftime("%d.%m.%Y")

        self.current_date_from = None
        self.current_date_to = None

        self.recent_oper_num = (
            7 if self.user_transactions is None else len(self.user_transactions.keys())
        )
        self.upcoming_oper_num = (
            7 if self.user_upcomings is None else len(self.user_upcomings.keys())
        )

        self.analysis_result = None

        self.init_section()

    def init_section(self):
        """
        Section initialization
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(0)

        # Title layout
        top_layout = QVBoxLayout()
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(50, 0, 50, 0)

        self.input_frame = QFrame()
        self.input_frame.setStyleSheet("border: 1px solid #b5c0c9; border-radius:10px")
        self.input_layout = QGridLayout(self.input_frame)

        # Type of analysis
        self.analysis_type_label = QLabel(self)
        self.analysis_type_label.setText("Type of analysis")
        self.analysis_type_label.setStyleSheet(
            "color: black; font-size: 12pt; padding:5px; border: 0px"
        )
        self.analysis_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.analysis_type_combo = QComboBox(self)
        self.analysis_type_combo.addItems(ANALYSIS_TYPES)
        self.analysis_type_combo.currentIndexChanged.connect(
            self.on_analysis_type_change
        )

        # Type of analysis
        self.category_type_label = QLabel(self)
        self.category_type_label.setText("Category")
        self.category_type_label.setStyleSheet(
            "color: black; font-size: 12pt; padding:5px; border: 0px"
        )
        self.category_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.category_type_combo = QComboBox(self)
        self.category_type_combo.addItems(
            list(
                dict.fromkeys(
                    [
                        category.get("Level_1")
                        for category in self.user_categories.values()
                    ]
                )
            )
            if not self.user_categories is None
            else []
        )

        # Date from
        self.date_from_label = QLabel(self)
        self.date_from_label.setText("Date from")
        self.date_from_label.setStyleSheet(
            "color: black; font-size: 12pt; padding:5px; border: 0px"
        )
        self.date_from_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_from_label.setContentsMargins(20, 0, 0, 0)

        self.date_from_edit = QDateEdit(self)
        self.date_from_edit.setCalendarPopup(True)
        self.date_from_edit.setDisplayFormat("MM.yyyy")
        self.date_from_edit.setCurrentSection(QDateTimeEdit.MonthSection)
        self.date_from_edit.setContentsMargins(0, 0, 20, 0)
        self.date_from_edit.dateChanged.connect(self.on_date_from_change)

        # Date to
        self.date_to_label = QLabel(self)
        self.date_to_label.setText("Date to     ")
        self.date_to_label.setStyleSheet(
            "color: black; font-size: 12pt; padding:5px; border: 0px"
        )
        self.date_to_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_to_label.setContentsMargins(20, 0, 0, 0)

        self.date_to_edit = QDateEdit(self)
        self.date_to_edit.setCalendarPopup(True)
        self.date_to_edit.setDisplayFormat("MM.yyyy")
        self.date_to_edit.setCurrentSection(QDateTimeEdit.MonthSection)
        self.date_to_edit.setContentsMargins(0, 0, 20, 0)
        self.date_to_edit.setDate(
            QDate().fromString(self.last_operation_date, "dd.MM.yyyy")
        )
        self.date_to_edit.dateChanged.connect(self.on_date_to_change)

        # Calculate button
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.calculate_btn.setMinimumHeight(60)
        self.calculate_btn.setMinimumWidth(130)
        self.calculate_btn.clicked.connect(lambda: self.create_analysis())

        self.input_layout.addWidget(
            self.analysis_type_label, 0, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.input_layout.addWidget(
            self.analysis_type_combo, 0, 1, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.input_layout.addWidget(
            self.category_type_label, 1, 0, alignment=Qt.AlignmentFlag.AlignLeft
        )
        self.input_layout.addWidget(
            self.category_type_combo, 1, 1, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.input_layout.addWidget(
            self.date_from_label, 0, 2, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.input_layout.addWidget(
            self.date_from_edit, 0, 3, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.input_layout.addWidget(
            self.date_to_label, 1, 2, alignment=Qt.AlignmentFlag.AlignRight
        )
        self.input_layout.addWidget(
            self.date_to_edit, 1, 3, alignment=Qt.AlignmentFlag.AlignVCenter
        )

        self.input_layout.addWidget(
            self.calculate_btn, 0, 4, 2, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        top_layout.addWidget(self.input_frame, 0)

        # Result layout (Table + chart)
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(0)

        self.init_categorical()
        self.init_aggregate()
        self.init_prognosis()

        self.result_stack = QStackedWidget()
        self.result_stack.addWidget(self.categorical_widget)
        self.result_stack.addWidget(self.aggregate_widget)
        self.result_stack.addWidget(self.prognosis_widget)

        bottom_layout.addWidget(self.result_stack)

        main_layout.addLayout(top_layout, 0)
        main_layout.addLayout(bottom_layout, 0)

        if not self.user_transactions is None and len(self.user_transactions) > 0:

            # Create default analysis charts for all types
            for analysis_type in ANALYSIS_TYPES:

                date_from = datetime.strptime(
                    f"01.{self.date_from_edit.text()}", "%d.%m.%Y"
                )

                date_to = datetime.strptime(
                    self.last_operation_date, "%d.%m.%Y"
                ) + relativedelta(day=31)

                if analysis_type == "Prognosis":
                    date_from = datetime.strptime(self.last_operation_date, "%d.%m.%Y")

                    date_to = datetime.strptime(
                        self.prognosis_date_to, "%d.%m.%Y"
                    ) + relativedelta(day=31)

                self.create_analysis(
                    analysis_type=analysis_type, date_from=date_from, date_to=date_to
                )

        self.analysis_type_combo.setCurrentText(self.user_def_analysis)

    def init_categorical(self):
        """
        Crete categorical analysis view
        """
        self.categorical_widget = QWidget()
        self.categorical_layout = QVBoxLayout(self.categorical_widget)
        self.categorical_layout.setSpacing(0)

        self.categorical_table = TableWidget(
            parent=self,
            row_num=7,
            col_num=len(CATEGORICAL_HEADERS),
            header_names=CATEGORICAL_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            editable=False,
        )
        self.categorical_layout.addWidget(self.categorical_table, 0)

    def init_aggregate(self):
        """
        Create monthly cashflow view
        """
        self.aggregate_widget = QWidget()
        self.aggregate_layout = QVBoxLayout(self.aggregate_widget)
        self.aggregate_layout.setSpacing(15)

        self.aggregate_table = TableWidget(
            parent=self,
            row_num=7,
            col_num=len(AGGREGATE_HEADERS),
            header_names=AGGREGATE_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            editable=False,
        )

        self.aggregate_layout.addWidget(self.aggregate_table, 0)

    def init_prognosis(self):
        """
        Create prognosis analysis view
        """
        self.prognosis_widget = QWidget()
        self.prognosis_layout = QVBoxLayout(self.prognosis_widget)
        self.prognosis_layout.setSpacing(15)

        self.prognosis_table = TableWidget(
            parent=self,
            row_num=7,
            col_num=len(PROGNOSIS_HEADERS),
            header_names=PROGNOSIS_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            editable=False,
        )

        self.prognosis_layout.addWidget(self.prognosis_table, 0)

    def on_date_from_change(self):
        """
        Set date to according to choosen analysis type.
        If prognosis type is choosen set it to last operation date.
        """
        date_from = datetime.strptime(f"01.{self.date_from_edit.text()}", "%d.%m.%Y")

        last_operation_date = datetime.strptime(
            self.last_operation_date, "%d.%m.%Y"
        ) + relativedelta(day=1)

        if (
            self.analysis_type_combo.currentText() == "Prognosis"
            and date_from < last_operation_date
        ):
            self.date_from_edit.setDate(
                QDate().fromString(
                    last_operation_date.strftime("%d.%m.%Y"), "dd.MM.yyyy"
                )
            )

    def on_date_to_change(self):
        """
        Block date to to be lower than date from.
        """
        date_from = datetime.strptime(f"01.{self.date_from_edit.text()}", "%d.%m.%Y")

        date_to = datetime.strptime(
            f"01.{self.date_to_edit.text()}", "%d.%m.%Y"
        ) + relativedelta(day=31)

        if date_to < date_from:
            self.date_to_edit.setDate(
                QDate().fromString(date_from.strftime("%d.%m.%Y"), "dd.MM.yyyy")
            )

    def on_analysis_type_change(self):
        """
        Set current analysis view and date for choosen type.
        For prognosis set date from as last operation date and date to as value + 2 years.
        For other analysis type set date to as last operation date and date from as remebered date.
        """
        self.category_type_label.setVisible(False)
        self.category_type_combo.setVisible(False)

        # Get date from
        date_from = datetime.strptime(f"01.{self.date_from_edit.text()}", "%d.%m.%Y")

        # Set current date from
        if date_from < datetime.strptime(self.last_operation_date, "%d.%m.%Y"):
            self.current_date_from = self.date_from_edit.text()

        # Set dates
        match self.analysis_type_combo.currentText():
            case "Categorical":
                self.category_type_label.setVisible(True)
                self.category_type_combo.setVisible(True)
                self.result_stack.setCurrentIndex(0)

                self.date_from_edit.setDate(
                    QDate().fromString(self.current_date_from, "dd.MM.yyyy")
                )
                self.date_to_edit.setDate(
                    QDate().fromString(self.last_operation_date, "dd.MM.yyyy")
                )
            case "Aggregate":
                self.result_stack.setCurrentIndex(1)

                self.date_from_edit.setDate(
                    QDate().fromString(self.current_date_from, "dd.MM.yyyy")
                )
                self.date_to_edit.setDate(
                    QDate().fromString(self.last_operation_date, "dd.MM.yyyy")
                )
            case "Prognosis":

                self.result_stack.setCurrentIndex(2)

                self.date_from_edit.setDate(
                    QDate().fromString(self.last_operation_date, "dd.MM.yyyy")
                )
                self.date_to_edit.setDate(
                    QDate().fromString(self.prognosis_date_to, "dd.MM.yyyy")
                )

    def update_operations(self, data, type):
        """
        Update data in table and on on the plot


        Args:
            data (dict): transaction
            type (str): type of operations
        """
        match type:
            case "Upcoming":
                self.user_upcomings = data
            case _:
                self.user_transactions = data

    def create_analysis(self, analysis_type=None, date_to=None, date_from=None):
        """
        Create analysis for choosen type and dates.

        Args:
            analysis_type (_type_, optional): Type  of analysis to make. Defaults to None.
            date_to (date, optional): Analysis date from. Defaults to None.
            date_from (date, optional): Analysis date to. Defaults to None.
        """
        if analysis_type is None:
            analysis_type = self.analysis_type_combo.currentText()

        if analysis_type in ["Categorical", "Aggregate"] and (
            self.user_transactions is None or len(self.user_transactions) == 0
        ):
            msg = "Please add at least one transaction to analize date!"
            ErrorBox(self, title="No categories!", msg=msg)
            return

        # Columns to get from databases
        columns_to_get = ["1_name", "2_date", "4_type", "5_category", "6_amount"]

        if not self.user_transactions is None and len(self.user_transactions) > 0:
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
        else:
            transactions = pd.DataFrame(columns=columns_to_get)

        transaction_summary = transactions.copy().groupby(["4_type"])["6_amount"].sum()

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
            self.current_acc_balance + (income - expense),
            2,
        )

        # Prepare upcomings database
        upcomings = None
        if not self.user_upcomings is None and len(self.user_upcomings) > 0:
            upcomings = (
                pd.DataFrame(self.user_upcomings)
                .T.reset_index(drop=True)
                .copy()[columns_to_get]
            )

            upcomings["2_date"] = upcomings["2_date"].apply(
                lambda x: datetime.strptime(x, "%d.%m.%Y")
            )
            upcomings["6_amount"] = upcomings["6_amount"].apply(
                lambda x: float(x.replace(",", ".").replace(" ", ""))
            )

        if date_from is None:
            date_from = datetime.strptime(
                f"01.{self.date_from_edit.text()}", "%d.%m.%Y"
            )

        if date_to is None:
            date_to = datetime.strptime(
                f"01.{self.date_to_edit.text()}", "%d.%m.%Y"
            ) + relativedelta(day=31)

        # Analyse data
        self.analysis_result = Analysis(
            analysis_type=analysis_type,
            date_from=date_from,
            date_to=date_to,
            transactions=transactions,
            upcomings=upcomings,
            category=self.category_type_combo.currentText(),
            account_balance=curr_acc_bal,
            average_revenue=self.monthly_net_salary,
            average_spendings=self.avg_monthly_expense,
        )

        # Set plot and table data to widgets
        match analysis_type:
            case "Categorical":
                self.categorical_table.update_table(
                    self.analysis_result.get_data_to_table()
                )
                try:
                    self.categorical_plot.deleteLater()
                except AttributeError:
                    pass

                self.categorical_plot = BarChart(
                    parent=self,
                    data=self.analysis_result.get_data_to_plot(),
                    title="Monthly expenses for category: {0}".format(
                        self.category_type_combo.currentText()
                    ),
                    legend=False,
                    x_label="Year - Month",
                    y_label="[{0}]".format(self.currency),
                    y_axis_visible=False,
                    gridlines=False,
                )

                self.categorical_layout.addWidget(self.categorical_plot, 2)
                self.categorical_layout.addWidget(self.categorical_table, 1)

            case "Aggregate":
                self.aggregate_table.update_table(
                    self.analysis_result.get_data_to_table()
                )
                try:
                    self.aggregate_plot.deleteLater()
                except AttributeError:
                    pass

                self.aggregate_plot = BarChart(
                    parent=self,
                    data=self.analysis_result.get_data_to_plot(),
                    title="Monthly cashflow",
                    legend=True,
                    x_label="Year - Month",
                    y_label="[{0}]".format(self.currency),
                    y_axis_visible=False,
                    gridlines=False,
                )

                self.aggregate_layout.addWidget(self.aggregate_plot, 2)
                self.aggregate_layout.addWidget(self.aggregate_table, 1)

            case "Prognosis":
                self.prognosis_table.update_table(
                    self.analysis_result.get_data_to_table()
                )
                try:
                    self.prognosis_plot.deleteLater()
                except AttributeError:
                    pass

                self.prognosis_plot = BarChart(
                    parent=self,
                    data=self.analysis_result.get_data_to_plot(),
                    title="Projected account balance for the next 14 months<sup>*</sup",
                    legend=False,
                    x_label="Year - Month",
                    y_label="[{0}]".format(self.currency),
                    y_axis_visible=False,
                    gridlines=False,
                    colors={
                        self.analysis_result.get_data_to_plot().columns[0]: "#66b8ff"
                    },
                    tootltip=CHART_TOOLTIPS.get(analysis_type),
                )

                self.prognosis_layout.addWidget(self.prognosis_plot, 2)
                self.prognosis_layout.addWidget(self.prognosis_table, 1)
