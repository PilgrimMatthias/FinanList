from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import json
import pandas as pd
from datetime import datetime

from finance_app.config import *
from finance_app.modules import TableWidget, EditTransaction, ErrorBox


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

        # Search box visibility bool
        self.search_box_visible = False

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
            sorting=False,
            filtering=True,
            id_column=True,
        )
        self.upcoming_operations_table.cellDoubleClicked.connect(self.show_transaction)

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
        self.search_box = QLineEdit()
        self.search_box.setMinimumHeight(40)
        self.search_box.setMinimumWidth(200)
        self.search_box.setVisible(self.search_box_visible)
        self.search_box.textChanged.connect(self.upcoming_operations_table.filter)

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
        main_layout.addWidget(self.upcoming_operations_table, 0)

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

    def update_upcoming_oper(self, data):
        """
        Method for updating operations table

        Args:
            data (dict): data to display on table
        """
        self.user_upcomings = data
        # Data prep
        data = pd.DataFrame(data).T.reset_index(drop=True)
        self.upcoming_operations_table.clear_table()

        if len(self.user_upcomings) > 0:
            data = data[
                [
                    col
                    for col in data.columns
                    if not "vendor" in col and not "type" in col
                ]
            ]
            data.columns = PLANNED_OPERATIONS_HEADERS

            # Update table data
            self.upcoming_operations_table.update_table(data)

    def show_transaction(self, row, columns):
        """
        Showing choosen transaction for user.

        Args:
            row (int): transaction row
            columns (int): _description_
        """
        # Get transaction data from table
        tr_number = (
            self.upcoming_operations_table.cellWidget(row, 0)
            .findChild(QCheckBox)
            .get_hidden_property()
        )
        selected_transaction = self.user_upcomings.get(str(tr_number))

        name = self.upcoming_operations_table.item(row, 1).text()
        date = self.upcoming_operations_table.item(row, 2).text().split("-")

        seller = selected_transaction.get("3_vendor")
        type = selected_transaction.get("4_type")

        date = "{0}.{1}.{2}".format(date[2], date[1], date[0])
        category = self.upcoming_operations_table.item(row, 3).text()
        amount = self.upcoming_operations_table.item(row, 4).data(
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
        oper_to_export = self.user_upcomings

        # Check if there are any selected operations
        if self.delete_btn.isVisible():
            selected_rows = self.upcoming_operations_table.get_selected_rows()

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
                        temp_transaction = self.user_upcomings.get(str(tr_num))

                        oper_to_export[str(tr_num)] = temp_transaction
        # Dialog to choose save path
        save_path = QFileDialog.getSaveFileName(
            self,
            self.tr("Save File"),
            "{0}{1}.xlsx".format(
                EXPORT_FILE_NAME, datetime.today().strftime("%d-%m-%Y")
            ),
            self.tr("Excel (*.xlsx);;Comma-separated values (*.csv)"),
        )

        if save_path is not None and (
            self.user_upcomings is not None and len(oper_to_export) > 0
        ):

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

    def on_select_click(self):
        """
        On select button click event.

        When clicked delete button and first id column is shown/hidden.
        """
        # Show/hide id column in table
        self.upcoming_operations_table.show_column(0)

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
        selected_rows = self.upcoming_operations_table.get_selected_rows()

        if len(selected_rows) == 0:
            msg = "No transactions where selected!\nSelect at least one operation!"
            ErrorBox(self, title="Nothing to delete!", msg=msg)
            return

        # Create transation dicts
        selected_tr_dict = {}
        for tr_num in selected_rows:
            temp_transaction = self.user_upcomings.get(str(tr_num))

            selected_tr_dict[str(tr_num)] = temp_transaction

        # Send transactions to delete
        self.update_transaction.emit(selected_tr_dict, "Delete-Upcoming")
