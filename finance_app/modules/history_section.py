from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime

from finance_app.config import *
from finance_app.modules import TableWidget, EditTransaction, ErrorBox, LineEdit


class HistorySection(QWidget):
    """
    History section where all past operations are displayed.
    User can:
        - Export data to csv or excel
    """

    update_transaction = Signal(dict, str)

    def __init__(
        self,
        current_acc_balance,
        currency,
        user_transactions,
        user_transactions_path,
        user_categories,
    ):
        super().__init__()

        # User data
        self.current_acc_balance = current_acc_balance
        self.currency = currency
        self.user_transactions = user_transactions
        self.user_transactions_path = user_transactions_path
        self.user_categories = user_categories

        self.recent_oper_num = (
            7 if self.user_transactions is None else len(self.user_transactions.keys())
        )

        self.row_nums = 12

        # Search box visibility bool
        self.search_box_visible = False

        self.init_section()

    def init_section(self):
        """
        Initialize section

        """
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.setSpacing(15)

        # Aktualny stan konta
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

        # Select transactions btn
        self.select_btn = QPushButton("Select")
        self.select_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.select_btn.setMinimumHeight(40)
        self.select_btn.setMinimumWidth(130)
        self.select_btn.clicked.connect(self.on_select_click)

        # Delete transactions btn
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setStyleSheet(
            "QPushButton {background-color: #ff3333; border-style: solid; border-color: #ff3333; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #ff8080; border-style: solid; border-color: #ff8080; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.delete_btn.setMinimumHeight(40)
        self.delete_btn.setMinimumWidth(130)
        self.delete_btn.setVisible(False)
        self.delete_btn.clicked.connect(self.delete_transactions)

        # Export transactions btn
        self.export_btn = QPushButton("Export")
        self.export_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setMinimumWidth(130)
        self.export_btn.clicked.connect(self.export_data)

        # Create report btn
        self.report_btn = QPushButton("Create report")
        self.report_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.report_btn.setMinimumHeight(40)
        self.report_btn.setMinimumWidth(130)

        # Table with categories
        self.user_operations_table = TableWidget(
            parent=self,
            row_num=self.recent_oper_num,
            col_num=len(RECENT_OPERATIONS_HEADERS),
            header_names=RECENT_OPERATIONS_HEADERS,
            font=QFont(
                "Notosans",
                10,
            ),
            data=pd.DataFrame(self.user_transactions).T.reset_index(drop=True),
            sorting=False,
            filtering=True,
            editable=False,
            id_column=True,
        )
        self.user_operations_table.cellDoubleClicked.connect(self.show_transaction)

        # Search button
        self.search_btn = QPushButton()
        self.search_btn.setIcon(QIcon(SEARCH_ICON_WHITE))
        self.search_btn.setStyleSheet(
            "QPushButton {background-color: #0085FC; border-style: solid; border-color: #0085FC; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;} "
            + "QPushButton::pressed {background-color: #4dacff; border-style: solid; border-color: #4dacff; border-width: 2px; border-radius: 10px; font-size: 10pt; color:white;}"
        )
        self.search_btn.setMinimumHeight(40)
        self.search_btn.setMinimumWidth(40)
        self.search_btn.clicked.connect(self.show_search)

        # Search edit box
        self.search_box = LineEdit(self)
        self.search_box.setMinimumHeight(40)
        self.search_box.setMinimumWidth(200)
        self.search_box.setVisible(self.search_box_visible)
        self.search_box.textChanged.connect(self.user_operations_table.filter)

        # Spacer for button layout
        self.spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Fixed)

        btn_layout.addWidget(self.select_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.delete_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.export_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addItem(self.spacer)
        btn_layout.addWidget(self.search_box, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        btn_layout.addWidget(self.search_btn, 0, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addWidget(self.curr_acc_label, 0)
        main_layout.addLayout(btn_layout, 0)
        main_layout.addWidget(self.user_operations_table, 0)

    def show_search(self):
        """
        Method for showing search text widget on search button click.

        If search button changes from visible to hidden it also clears its content.
        """
        if self.search_box_visible:
            self.search_box_visible = False
            self.search_box.setText("")
        else:
            self.search_box_visible = True

        self.search_box.setVisible(self.search_box_visible)

    def update_operations(self, data):
        """
        Update dara in table

        Args:
            data (dict): data to update in table
        """
        self.user_transactions = data

        updated_df = pd.DataFrame(data).T.reset_index(drop=True)
        self.user_operations_table.clear_table()

        if len(self.user_transactions) > 0:
            updated_df.columns = RECENT_OPERATIONS_HEADERS
            self.user_operations_table.update_table(updated_df)

    def show_transaction(self, row, columns):
        """
        Showing choosen transaction for user.

        Args:
            row (int): transaction row
            columns (int): _description_
        """
        # Get transaction data from table
        tr_number = (
            self.user_operations_table.cellWidget(row, 0)
            .findChild(QCheckBox)
            .get_hidden_property()
        )
        name = self.user_operations_table.item(row, 1).text()
        date = self.user_operations_table.item(row, 2).text().split("-")
        date = "{0}.{1}.{2}".format(date[2], date[1], date[0])
        seller = self.user_operations_table.item(row, 3).text()
        type = self.user_operations_table.item(row, 4).text()
        category = self.user_operations_table.item(row, 5).text()
        amount = self.user_operations_table.item(row, 6).data(
            Qt.ItemDataRole.UserRole + 1
        )

        # Choosen transaction window
        self.transaction_edit = EditTransaction(
            number=tr_number,
            name=name,
            date=date,
            seller=seller,
            type=type,
            category=category,
            amount=amount,
            user_categories=self.user_categories,
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
        oper_to_export = self.user_transactions

        # Check if there are any selected operations
        if self.delete_btn.isVisible():
            selected_rows = self.user_operations_table.get_selected_rows()

            if len(selected_rows) > 0:
                # Confirmation box
                confirmation = QMessageBox.question(
                    self,
                    "Export selected",
                    "Do you want to export the selected operations?",
                    defaultButton=QMessageBox.StandardButton.No,
                )

                # If exprot selected operations than create dict with these operations to export
                if confirmation == QMessageBox.StandardButton.Yes:
                    oper_to_export = {}

                    for tr_num in selected_rows:
                        temp_transaction = self.user_transactions.get(str(tr_num))

                        oper_to_export[str(tr_num)] = temp_transaction

        save_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save File"),
            "{0}{1}.xlsx".format(
                EXPORT_FILE_NAME, datetime.today().strftime("%d-%m-%Y")
            ),
            self.tr("Excel (*.xlsx);;Comma-separated values (*.csv)"),
        )

        if save_path is not None:

            # Getting choosen path and extension by user
            extension = save_path[1].split(".")[-1].replace(")", "")
            file_path = save_path[0]
            if extension not in file_path:
                file_path += "." + extension

            # Data prep (to dataframe)
            data_to_save = pd.DataFrame(oper_to_export).T.reset_index(drop=False)
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

    def on_select_click(self):
        """
        On select button click event.

        When clicked delete button and first id column is shown/hidden.
        """
        # Show/hide id column in table
        self.user_operations_table.show_column(0)

        # Show/hide delete button
        if self.delete_btn.isVisible():
            self.delete_btn.setVisible(False)
        else:
            self.delete_btn.setVisible(True)

    def delete_transactions(self):
        """
        Delete transactions event

        When clicked selected transactions by user will be deleted from database.
        """
        # Selected rows
        selected_rows = self.user_operations_table.get_selected_rows()

        if len(selected_rows) == 0:
            msg = "No transactions where selected!\nSelect at least one operation!"
            ErrorBox(self, title="Nothing to delete!", msg=msg)
            return

        # Deletion confirmation box
        confirmation = QMessageBox.question(
            self,
            "Confirmation",
            "Delete selected transactions?\nThis will permamently delete them!",
            defaultButton=QMessageBox.StandardButton.No,
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            # Create transation dicts
            selected_tr_dict = {}
            for tr_num in selected_rows:
                temp_transaction = self.user_transactions.get(str(tr_num))

                selected_tr_dict[str(tr_num)] = temp_transaction

            # Send transactions to delete
            self.update_transaction.emit(selected_tr_dict, "Delete-Transaction")
