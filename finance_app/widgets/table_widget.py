from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from finance_app.utils import is_date, is_number


class TableWidget(QTableWidget):
    """
    Custom Table Widget with possibility to clear, add and get data from table.
    """

    def __init__(
        self,
        parent=None,
        row_num=1,
        col_num=1,
        header_names=[""],
        font=QFont(),
        data=None,
        editable=True,
        sorting=False,
        val_formatter="double",
        val_formatter_col_disable=None,
    ):
        super().__init__()

        self.row_num = row_num
        self.col_num = col_num
        self.header_names = header_names
        self.text_font = font
        self.data = data
        self.editable = editable
        self.sorting = sorting
        self.val_formatter = val_formatter
        self.val_formatter_col_disable = val_formatter_col_disable

        self.rounded_style = """
            QTableWidget {
                border: 1px solid #999999;
                border-radius: 5px;
                background-color: #FFFFFF;
                color: #000000;
                gridline-color: #999999;
                font-size: 10pt;
            }
            QHeaderView::section {
                font-size: 10pt;
            }
            QTableView::item  {
                background-color: #FFFFFF;
                color: #000000;
                gridline-color: #999999;
                font-size: 10pt;
            }
            QLineEdit{
                border-width: 1px; 
                border-radius: 1px; 
            }
        """

        self.view_flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled

        self.edit_flags = Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled

        self.init_table()

    def init_table(self):
        """
        Initialize table
        """
        # Set basic table variables
        self.setRowCount(self.row_num)
        self.setColumnCount(self.col_num)
        self.setFont(self.text_font)
        self.setHorizontalHeaderLabels(self.header_names)
        self.horizontalHeader().setMinimumHeight(40)

        self.setContentsMargins(0, 0, 0, 0)

        # Set sorting
        if self.sorting:
            self.setSortingEnabled(True)
            self.horizontalHeader().setSectionsClickable(True)

        # Set table beahaviour
        self.verticalHeader().setVisible(False)
        self.resizeRowsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.setWordWrap(True)  # Zawijanie tekstu
        self.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalHeader().setDefaultSectionSize(40)

        # Table setyle
        self.setStyleSheet(self.rounded_style)

        # Set headerers
        for header in range(self.horizontalHeader().count()):
            header_item = self.horizontalHeaderItem(header)
            header_item.setBackground(QColor("#e6e6e6"))
            header_item.setForeground(QColor("#000000"))
            self.setHorizontalHeaderItem(header, header_item)

        # Add data if provided
        if self.data is not None:
            for row in self.data.index:
                for column in range(len(self.data.columns)):
                    value = self.data.iloc[row, column]
                    item = QTableWidgetItem()
                    item.setFlags(self.view_flags)
                    if self.editable:
                        item.setFlags(self.edit_flags)
                    item.setFont(self.text_font)

                    # Set value display role (for sorting)
                    if is_number(value):  # number
                        item.setData(Qt.ItemDataRole.UserRole + 1, value)

                        item.setData(
                            Qt.ItemDataRole.EditRole,
                            float(value.replace(",", ".").replace(" ", "")),
                        )

                    elif is_date(value, "%d.%m.%Y"):  # date
                        item.setData(Qt.ItemDataRole.UserRole + 1, value)

                        value = value.split(".")
                        value = QDate(int(value[2]), int(value[1]), int(value[0]))

                        item.setData(
                            Qt.ItemDataRole.EditRole,
                            value,
                        )

                    else:
                        item.setData(Qt.ItemDataRole.UserRole + 1, value)
                        item.setData(
                            Qt.ItemDataRole.EditRole,
                            value,
                        )

                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.setItem(row, column, item)

        self.setContentsMargins(0, 0, 0, 0)

        self.itemChanged.connect(self.double_formatter)

    def update_headers(self, headers):
        """
        Update columns in table

        Args:
            headers (list): headers to add to table
        """
        self.setColumnCount(len(headers))  # Col num
        self.setHorizontalHeaderLabels(headers)  # Setting header names

        # Formatting headers
        for header in range(self.horizontalHeader().count()):
            header_item = self.horizontalHeaderItem(header)
            header_item.setBackground(QColor("#e6e6e6"))
            header_item.setForeground(QColor("#000000"))
            self.setHorizontalHeaderItem(header, header_item)

    def update_table(self, data):
        """
        Updating table items with new data

        Args:
            data : data to show in table
        """
        # Disabling sorting
        if self.isSortingEnabled():
            self.setSortingEnabled(False)

        # Update columns in table
        if len(data.columns) > self.col_num:
            self.update_headers(data.columns)

        self.setRowCount(len(data.index))  # Set row num

        for row in data.index:
            for column in range(len(data.columns)):
                value = data.iloc[row, column]
                item = QTableWidgetItem()
                item.setFlags(self.view_flags)
                if self.editable:
                    item.setFlags(self.edit_flags)
                item.setFont(self.text_font)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Set value display role (for sorting)
                if is_number(value):  # number
                    # Actual data
                    item.setData(Qt.ItemDataRole.UserRole + 1, value)

                    # Edit role data for sorting
                    item.setData(
                        Qt.ItemDataRole.EditRole,
                        float(value.replace(",", ".").replace(" ", "")),
                    )

                elif is_date(value, "%d.%m.%Y"):  # date
                    # Actual data
                    item.setData(Qt.ItemDataRole.UserRole + 1, value)

                    value = value.split(".")
                    value = QDate(int(value[2]), int(value[1]), int(value[0]))

                    # Edit role data for sorting
                    item.setData(
                        Qt.ItemDataRole.EditRole,
                        value,
                    )

                else:  # Other values
                    item.setData(Qt.ItemDataRole.UserRole + 1, value)
                    item.setData(
                        Qt.ItemDataRole.EditRole,
                        value,
                    )
                self.setItem(row, column, item)

        self.data = data

        # Enabling sorting
        if self.sorting:
            self.setSortingEnabled(True)

    def clear_table(self):
        """
        Delete data from table
        """
        self.row_num = 0
        self.setRowCount(self.row_num)

        self.data = None

    def double_formatter(self, item):
        """
        Formatter for items in table

        Args:
            item (QTableWidgetItem): Table item
        """
        try:
            number = float(item.text().replace(" ", "").replace(",", "."))

            # Value formatting
            if number.is_integer():
                formatted_number = f"{int(number)}".replace(",", "")
            else:
                formatted_number = f"{number:,.2f}".replace(",", " ").replace(".", ",")

            item.setText(formatted_number)
        except ValueError:
            pass
