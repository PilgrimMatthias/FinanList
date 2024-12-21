from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime

from finance_app.widgets.table_widget import TableWidget
from finance_app.modules.add_windows import EditTransaction
from finance_app.config import *
from finance_app.utils import filter_func


class UpcomingSection(QWidget):
    """
    Upcoming sections is section were all planned operations will be stored and displayed in table.
    """

    update_transaction = Signal(dict, str)  # Signal for data update

    def __init__(
        self,
        current_acc_balance,
        currency,
        user_upcomings,
        user_upcomings_path,
        user_categories,
    ):
        super().__init__()

        # User data
        self.current_acc_balance = current_acc_balance
        self.currency = currency
        self.user_upcomings = user_upcomings
        self.user_upcomings_path = user_upcomings_path
        self.user_categories = user_categories

        self.user_upcomings_to_table = pd.DataFrame(self.user_upcomings).T.reset_index(
            drop=True
        )
        self.user_upcomings_to_table = self.user_upcomings_to_table[
            [
                col
                for col in self.user_upcomings_to_table.columns
                if not "vendor" in col and not "type" in col
            ]
        ]

        self.upcoming_oper_num = (
            7
            if self.user_upcomings_to_table is None
            else len(self.user_upcomings_to_table.index)
        )

        self.row_nums = 12

        self.init_section()

    def init_section(self):
        """
        Section initialization
        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(15)

        # Current account balance
        self.curr_acc_label = QLabel(self)
        self.curr_acc_label.setText(
            "Account balance as of {0}: {1} {2}".format(
                datetime.today().strftime("%d-%m-%Y"),
                str(self.current_acc_balance).replace(".", ","),
                self.currency,
            )
        )
        self.curr_acc_label.setContentsMargins(0, 0, 0, 0)
        self.curr_acc_label.setStyleSheet(
            "color: black; font-size: 18pt; border: 1px solid #b5c0c9; border-radius:10px; padding:10px;"
        )
        self.curr_acc_label.setWordWrap(True)
        self.curr_acc_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Btn layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Edit transactions btn
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.edit_btn.setMinimumHeight(40)
        self.edit_btn.setMinimumWidth(130)

        # Export transactions btn
        self.export_btn = QPushButton("Export")
        self.export_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setMinimumWidth(130)
        self.export_btn.clicked.connect(self.export_data)

        btn_layout.addWidget(self.export_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        # Table with categories
        self.upcoming_operations_table = TableWidget(
            parent=self,
            row_num=self.upcoming_oper_num,
            col_num=len(PLANNED_OPERATIONS_HEADERS),
            header_names=PLANNED_OPERATIONS_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            data=pd.DataFrame(self.user_upcomings_to_table).reset_index(drop=True),
            editable=False,
            sorting=True,
        )
        self.upcoming_operations_table.cellDoubleClicked.connect(self.show_transaction)

        main_layout.addWidget(self.curr_acc_label, 0)
        main_layout.addLayout(btn_layout, 0)
        main_layout.addWidget(self.upcoming_operations_table, 0)

    def update_upcoming_oper(self, data):
        """
        Method for updating operations table

        Args:
            data (dict): data to display on table
        """
        # Data prep
        data = pd.DataFrame(data).T.reset_index(drop=True)
        data = data[
            [col for col in data.columns if not "vendor" in col and not "type" in col]
        ]

        # Update table data
        self.upcoming_operations_table.clear_table()
        self.upcoming_operations_table.update_table(data)

    def show_transaction(self, row, columns):
        """
        Showing choosen transaction for user.

        Args:
            row (int): transaction row
            columns (int): _description_
        """
        # Get transaction data from table
        name = self.upcoming_operations_table.item(row, 0).text()
        date = self.upcoming_operations_table.item(row, 1).text().split("-")

        date = "{0}.{1}.{2}".format(date[2], date[1], date[0])
        category = self.upcoming_operations_table.item(row, 2).text()
        amount = self.upcoming_operations_table.item(row, 3).data(
            Qt.ItemDataRole.UserRole + 1
        )

        # Get transaction from database
        selected_transaction = {
            key: val
            for key, val in self.user_upcomings.items()
            if filter_func(
                pair={
                    name_val: text_val
                    for name_val, text_val in val.items()
                    if not "vendor" in name_val and not "type" in name_val
                },
                condition=[name, date, category, amount],
            )
        }
        tr_number = list(selected_transaction.keys())[0]

        # Choosen transaction window
        self.transaction_edit = EditTransaction(
            number=tr_number,
            name=name,
            date=date,
            seller=selected_transaction.get(tr_number).get("3_vendor"),
            type=selected_transaction.get(tr_number).get("4_type"),
            category=category,
            amount=amount,
            user_categories=[
                category.get("Name") for category in self.user_categories.values()
            ],
        )
        self.transaction_edit.show()  # show window

        # Connect signals from EditTransaction
        self.transaction_edit.send_transaction.connect(self.get_transaction)

    @Slot(dict, str, str)
    def get_transaction(self, transaction, type_old, type_new):
        """
        Method for getting transaction when updated and passing it for update database.

        Args:
            transaction (dict): transaction values
            type_old (str): old transaction type
            type_new (str): new transaction type
        """
        type = ""

        if type_new == "Delete":
            type = "Delete-{0}".format(type_old)
        else:
            if type_new == type_old:
                match type_new:
                    case "Upcoming":
                        type = "Update-Upcoming"
                    case _:
                        type = "Update-Transaction"
            else:
                match type_old:
                    case "Upcoming":
                        pass
                    case _:
                        type_old = "Transaction"

                match type_new:
                    case "Upcoming":
                        pass
                    case _:
                        type_new = "Transaction"
                type = "Update-{0}to{1}".format(type_old, type_new)

        self.update_transaction.emit(transaction, type)  # emit signal

    def export_data(self):
        """
        Method for exporting data to csv or excel to user choosen path.
        """
        # Dialog to choose save path
        save_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save File"),
            "",
            self.tr("Comma-separated values (*.csv);;Excel (*.xlsx)"),
        )

        if save_path is not None:

            # Getting choosen path and extension by user
            extension = save_path[1].split(".")[-1].replace(")", "")
            file_path = save_path[0]
            if extension not in file_path:
                file_path += "." + extension

            # Data prep (to dataframe)
            data_to_save = pd.DataFrame(self.user_upcomings).T.reset_index(drop=False)
            data_to_save.columns = ["Operation number"] + [
                col.replace("\n", " ") for col in RECENT_OPERATIONS_HEADERS
            ]
            data_to_save["Operation number"] = range(1, len(data_to_save) + 1)

            # Data save by extension type
            match extension:
                case "csv":
                    data_to_save.to_csv(file_path, index=False, decimal=",", sep=";")
                case "xlsx":
                    data_to_save.to_excel(file_path, index=False)