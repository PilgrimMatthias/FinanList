from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from finance_app.config import ASCENDING_ICON, DESCENDING_ICON, FILTER_ICON

from finance_app.widgets import CheckBoxWidget, is_date, is_number


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
        filtering=False,
        val_formatter="double",
        val_formatter_col_disable=None,
        id_column=False,
    ):
        super().__init__()

        self.row_num = row_num
        self.col_num = col_num
        self.header_names = header_names
        self.text_font = font
        self.data = data
        self.editable = editable
        self.sorting = sorting
        self.filtering = filtering
        self.val_formatter = val_formatter
        self.val_formatter_col_disable = val_formatter_col_disable
        self.id_column = id_column

        if self.id_column:
            self.col_num += 1
            self.header_names = [""] + self.header_names

        self.id_checkboxes = []  # list of checkboxes in ID column

        self.col = 0
        self.filter_num = 0  # current filter num
        self.keywords = dict([[i, []] for i in range(self.columnCount())])

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
            QTableWidget::indicator{
                width:15px;
                height:15px;
                margin: 5px 5px 5px 5px;
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

        if self.id_column:
            for row in range(self.rowCount()):
                check_box_widget = QWidget()
                check_box_laout = QHBoxLayout(check_box_widget)
                check_box = CheckBoxWidget(
                    widget_text=row,
                    is_text_hidden=True,
                    hidden_propert_name="id_operation",
                )
                check_box_laout.addWidget(
                    check_box, alignment=Qt.AlignmentFlag.AlignCenter
                )

                self.id_checkboxes.append(check_box)

                self.setCellWidget(row, 0, check_box_widget)

            self.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.ResizeToContents
            )

            self.hideColumn(0)

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
                        number = float(value.replace(",", ".").replace(" ", ""))

                        # Value formatting
                        if number.is_integer():
                            formatted_number = f"{int(number):,}".replace(",", " ")
                        else:
                            formatted_number = f"{number:,.2f}".replace(
                                ",", " "
                            ).replace(".", ",")

                        # Actual data
                        item.setData(Qt.ItemDataRole.UserRole + 1, formatted_number)

                        # Edit role data for sorting
                        item.setData(
                            Qt.ItemDataRole.EditRole,
                            number,
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

                    if self.id_column:
                        self.setItem(row, column + 1, item)
                    else:
                        self.setItem(row, column, item)

        self.setContentsMargins(0, 0, 0, 0)

        if self.filtering:
            self.horizontalHeader().sectionClicked.connect(self.on_header_click)
            self.keywords = dict([[i, []] for i in range(self.columnCount())])

    def update_headers(self, headers):
        """
        Update columns in table

        Args:
            headers (list): headers to add to table
        """
        self.col_num = len(headers)
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
        if self.id_column:
            columns = [""]
            columns.extend(data.columns)
            self.update_headers(columns)
            columns = None
        else:
            self.update_headers(data.columns)

        self.setRowCount(len(data.index))  # Set row num

        self.id_checkboxes = []

        for row in range(self.rowCount()):
            # for column in range(len(data.columns)):
            for column in range(self.columnCount()):

                if self.id_column and column == 0:
                    check_box_widget = QWidget()
                    check_box_laout = QHBoxLayout(check_box_widget)
                    check_box = CheckBoxWidget(
                        widget_text=row,
                        is_text_hidden=True,
                        hidden_propert_name="id_operation",
                    )
                    check_box_laout.addWidget(
                        check_box, alignment=Qt.AlignmentFlag.AlignCenter
                    )

                    self.id_checkboxes.append(check_box)

                    self.setCellWidget(row, 0, check_box_widget)

                else:
                    item = QTableWidgetItem()
                    value = data.iloc[row, column - (1 if self.id_column else 0)]

                    item.setFlags(self.view_flags)
                    if self.editable:
                        item.setFlags(self.edit_flags)
                    item.setFont(self.text_font)

                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # Set value display role (for sorting)
                    if is_number(value):  # number
                        number = float(value.replace(",", ".").replace(" ", ""))

                        # Value formatting
                        if number.is_integer():
                            formatted_number = f"{int(number):,}".replace(",", " ")
                        else:
                            formatted_number = f"{number:,.2f}".replace(
                                ",", " "
                            ).replace(".", ",")

                        # Actual data
                        item.setData(Qt.ItemDataRole.UserRole + 1, formatted_number)

                        # Edit role data for sorting
                        item.setData(
                            Qt.ItemDataRole.EditRole,
                            number,
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

    def show_column(self, col_num):
        if self.isColumnHidden(col_num):
            self.showColumn(col_num)
        else:
            self.hideColumn(col_num)

    def get_selected_rows(self):
        selected_rows = []

        for row in range(self.rowCount()):
            row_widget = self.cellWidget(row, 0).findChild(QCheckBox)
            if row_widget.isChecked():
                selected_rows.append(row_widget.get_hidden_property())

        return selected_rows

    def filter(self, filter_text):
        """
        Method for filtering table based on provided text.
        Any cell row that contains filtered text will be shown, every other will be hidden.

        Args:
            filter_text (str): Text to search in table
        """
        col_list = range(self.columnCount())
        if self.id_column:
            col_list = range(1, self.columnCount())

        for i in range(self.rowCount()):
            for j in col_list:
                item = self.item(i, j)

                # Check if cell text matches filtered text
                match = filter_text.lower() not in item.text().lower()

                # Hide row
                self.setRowHidden(i, match)
                if not match:
                    break

    def on_header_click(self, column):
        """
        Method used for creation of filter menu with features:
            - Sort ascending and descending
            - List with possible options for filtering
            - Ok and cancel buttons
        """
        # Unique values for filter list
        data_unique = []

        # Check box list
        self.check_boxes = []

        # Column which method was invoked from
        self.col = column

        # Menu
        self.filter_menu = QMenu(self)
        self.filter_menu.setStyleSheet(
            """
            QMenu{
            border: 1px solid #b5c0c9;
            border-radius:10px;}
            """
        )

        # Sort widget layout
        sort_widget = QWidget(self)
        sort_layout = QVBoxLayout(sort_widget)

        # Ascending sort btn
        self.asc_sort_btn = QPushButton("Sort lowest to highest")
        self.asc_sort_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #899ba9; border-width: 1px; border-radius: 10px; font-size: 10pt; color:#899ba9;}"
        )
        self.asc_sort_btn.setMinimumHeight(30)
        self.asc_sort_btn.setMinimumWidth(175)
        self.asc_sort_btn.setIcon(QIcon(ASCENDING_ICON))
        self.asc_sort_btn.clicked.connect(
            lambda: self.sortByColumn(column, Qt.AscendingOrder)
        )

        # Descending sort btn
        self.desc_sort_btn = QPushButton("Sort highest to lowest")
        self.desc_sort_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #bfbfbf; border-width: 1px; border-radius: 10px; font-size: 10pt; color:#bfbfbf;}"
        )
        self.desc_sort_btn.setMinimumHeight(30)
        self.desc_sort_btn.setMinimumWidth(175)
        self.desc_sort_btn.setIcon(QIcon(DESCENDING_ICON))
        self.desc_sort_btn.clicked.connect(
            lambda: self.sortByColumn(column, Qt.DescendingOrder)
        )

        search_and_clear_widget = QWidget()
        search_and_clear_layout = QHBoxLayout(search_and_clear_widget)
        search_and_clear_layout.setContentsMargins(0, 0, 0, 0)

        # Search edit box
        self.search_box = QLineEdit()
        self.search_box.setMinimumHeight(30)
        self.search_box.setMinimumWidth(135)
        self.search_box.setStyleSheet(
            "background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;"
        )
        self.search_box.textChanged.connect(self.search_menu)

        # Clear filters button
        self.clear_filters_btn = QPushButton()
        self.clear_filters_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #bfbfbf; border-width: 1px; border-radius: 10px; font-size: 10pt; color:#bfbfbf;}"
        )
        self.clear_filters_btn.setMinimumHeight(30)
        self.clear_filters_btn.setMinimumWidth(30)
        self.clear_filters_btn.setIcon(QIcon(FILTER_ICON))
        self.clear_filters_btn.clicked.connect(self.clear_filters)

        search_and_clear_layout.addWidget(self.search_box)
        search_and_clear_layout.addWidget(self.clear_filters_btn)

        # Horizontal line
        self.horizontal_line = QFrame()
        self.horizontal_line.setFrameShape(QFrame.HLine)
        self.horizontal_line.setFrameShadow(QFrame.Sunken)
        self.horizontal_line.setMinimumHeight(1)
        self.horizontal_line.setStyleSheet(
            "border: 2px solid #b5c0c9; border-top:0px; border-right:0px; border-left:0px;"
        )

        # Add btn to  layout
        sort_layout.addWidget(self.asc_sort_btn, 0)
        sort_layout.addWidget(self.desc_sort_btn, 0)
        sort_layout.addWidget(search_and_clear_widget, 0)
        sort_layout.addWidget(self.horizontal_line, 0)

        # Layout with checkboxes for filtering
        filter_widget = QWidget(self)
        check_box_layout = QVBoxLayout(filter_widget)

        # Select all checkboxes widget
        self.select_all_box = CheckBoxWidget(
            widget_text="Select all", checked=True, box_style="small"
        )
        self.select_all_box.stateChanged.connect(self.select_all)

        check_box_layout.addWidget(self.select_all_box, 0)

        # Setting number of columns with filters applied
        filtered_column_count = 0
        for key in self.keywords.keys():
            column_keywords = self.keywords.get(key)
            if len(column_keywords) > 0 and key != column:
                filtered_column_count += 1

        # Row list to filter
        row_list = range(self.rowCount())

        # Add check boxes for options in choosen column
        for row in row_list:  # iterate through all rows
            filter_count = 0

            # Check if item in column (not in current menu col) and row is in keywords
            if self.filter_num > 0:
                for col_num in list(self.keywords.keys())[1:]:
                    item = self.item(row, col_num)  # get item

                    if (
                        item.text() in self.keywords.get(col_num)
                        and len(self.keywords.get(col_num)) > 0
                        and col_num != column
                    ):
                        filter_count += 1

            item = self.item(row, column)  # get item

            # Create checkbox if it is not in unique list
            if item.text() not in data_unique and filter_count == filtered_column_count:
                data_unique.append(item.text())

                # Checkbox widget
                check_box = CheckBoxWidget(
                    widget_text=item.text(), checked=True, box_style="small"
                )

                # Block state change signal in widget select_all_box
                blocker = QSignalBlocker(self.select_all_box)
                blocker.reblock()

                # Uncheck box if item text is not in in keywords
                if (item.text() not in self.keywords.get(column)) and (
                    len(self.keywords.get(column)) > 0
                ):

                    check_box.setChecked(False)
                    self.select_all_box.setChecked(False)

                # Unblock state change signal in widget select_all_box
                blocker.unblock()
                del blocker

                self.check_boxes.append(check_box)
                check_box_layout.addWidget(check_box, 0)

        # Spacer for button layout
        spacer = QSpacerItem(2, 2, QSizePolicy.Expanding, QSizePolicy.Expanding)
        check_box_layout.addItem(spacer)

        # Create scroll area
        scroll_area = QScrollArea()

        # Set Vertical and Horizontal scroll bar visibility
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(True)  # set scroll area as resizable
        scroll_area.setWidget(filter_widget)  # set widget for scroll area
        scroll_area.setMaximumHeight(245)
        scroll_area.setStyleSheet(
            """
            QScrollArea{
                border: 0px;
            }

            /* SCROLLBAR STYLE*/
            QScrollBar:vertical{
                border: 0px solid white;
                border-right: 1px solid #bfbfbf;
                border-left: 1px solid #bfbfbf;
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
                border-top-right-radius: 0px; 
                subcontrol-position: top;
                subcontrol-origin: margin;
                image: url(images:up_icon.png)
            }

            /* SCROLLBAR BOTTOM BUTTON STYLE */
            QScrollBar::add-line:vertical {
                border: 1px solid #bfbfbf;
                border-bottom-right-radius: 0px; 
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
        """
        )

        btn_widget = QWidget(self)
        btn_layout = QGridLayout(btn_widget)

        # Ascending sort btn
        self.ok_btn = QPushButton("Ok")
        self.ok_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #bfbfbf; border-width: 1px; border-radius: 10px; font-size: 10pt; color:#bfbfbf;}"
        )
        self.ok_btn.clicked.connect(self.menu_close)

        # Descending sort btn
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setStyleSheet(
            "QPushButton {background-color: white; border-style: solid; border-color: #a6a6a6; border-width: 1px; border-radius: 10px; font-size: 10pt; color:black;} "
            + "QPushButton::pressed {background-color: white; border-style: solid; border-color: #bfbfbf; border-width: 1px; border-radius: 10px; font-size: 10pt; color:#bfbfbf;}"
        )
        self.cancel_btn.clicked.connect(self.filter_menu.close)

        # Horizontal line 2
        self.horizontal_line_2 = QFrame()
        self.horizontal_line_2.setFrameShape(QFrame.HLine)
        self.horizontal_line_2.setFrameShadow(QFrame.Sunken)
        self.horizontal_line_2.setMinimumHeight(1)
        self.horizontal_line_2.setStyleSheet(
            "border: 2px solid #b5c0c9; border-top:0px; border-right:0px; border-left:0px;"
        )

        btn_layout.addWidget(
            self.horizontal_line_2,
            0,
            1,
            1,
            2,
        )
        btn_layout.addWidget(
            self.ok_btn,
            2,
            1,
            1,
            1,
        )
        btn_layout.addWidget(
            self.cancel_btn,
            2,
            2,
            1,
            1,
        )

        # Create a QWidgetAction to add custom widgets to the QMenu
        sort_action = QWidgetAction(self)
        sort_action.setDefaultWidget(sort_widget)
        sort_action.setCheckable(True)

        filter_action = QWidgetAction(self)
        filter_action.setDefaultWidget(scroll_area)
        filter_action.setCheckable(True)

        btn_action = QWidgetAction(self)
        btn_action.setDefaultWidget(btn_widget)
        btn_action.setCheckable(True)

        # Add the QWidgetAction to the dropdown menu
        self.filter_menu.addAction(sort_action)
        self.filter_menu.addAction(filter_action)
        self.filter_menu.addAction(btn_action)

        headerPos = self.mapToGlobal(self.horizontalHeader().pos())
        posY = headerPos.y() + self.horizontalHeader().height()
        posX = headerPos.x() + self.horizontalHeader().sectionPosition(column)
        self.filter_menu.exec(QPoint(posX, posY))

    def select_all(self, state):
        """
        Select all chechboxes in menu with "Selectl all" box

        Args:
            state (check state): state of select all checkbox
        """
        for checkbox in self.check_boxes:
            checkbox.setChecked(Qt.Checked == Qt.CheckState(state))

    def filter_data(self):
        """
        Filter method used for getting all checked boxes and setting only rows that contains value from keyword list.

        Filtering algorythm:
            1. Create list of choosen keywords from checkboxes.
            2. Show or hide checkboxes if cell value is in keyword for particular column keywords


        """
        # Checked keywords from menu
        col_keywords = []

        # Setting filtration list with choosen value from menu
        checked_checkboxes = 0
        for element in self.check_boxes:
            if element.isChecked():
                col_keywords.append(element.text())
                checked_checkboxes += 1

        self.keywords[self.col] = col_keywords

        # Setting number of columns with filters applied
        filtered_column_count = 0

        for column in self.keywords.keys():
            column_keywords = self.keywords.get(column)
            if len(column_keywords) > 0:
                filtered_column_count += 1

        # List of rows to check
        row_list = range(self.rowCount())

        # List of columns to check
        col_list = range(self.columnCount())
        if self.id_column:
            col_list = range(1, self.columnCount())

        self.filter_num += 1

        for i in row_list:
            # Number of filtered columns in row
            show_row = 0
            for j in col_list:
                item = self.item(i, j)

                # Check if item text is in filtration list for column
                if item.text() in self.keywords.get(j):
                    show_row += 1

            # Show row if number of filteres meets number of filtered columns in whole table
            if show_row == filtered_column_count:
                self.showRow(i)
            else:
                self.hideRow(i)

        # Clear keywords for column if all checkboxes are checked
        if checked_checkboxes == len(self.check_boxes):
            self.keywords[self.col] = []
            self.filter_num -= 1

    def clear_filters(self):
        """
        Clear all current filteres and set all show all rows
        """
        for i in range(self.rowCount()):
            self.setRowHidden(i, False)

    def search_menu(self, filter_text):
        """
        Show/hide menu filters that contain provided text

        Args:
            filter_text (string): filtration text
        """
        for checkbox in self.check_boxes:
            if filter_text.lower() in checkbox.text().lower():
                checkbox.show()
                checkbox.setChecked(True)
                if self.select_all_box.isChecked():
                    self.select_all_box.setChecked(False)
            else:
                checkbox.hide()
                checkbox.setChecked(False)

    def menu_close(self):
        """
        Close menu event.
        Table is filtered and menu is closed.
        """
        if len(self.check_boxes) > 1:
            self.filter_data()
        self.filter_menu.close()
