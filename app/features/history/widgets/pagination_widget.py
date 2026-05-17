from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Signal, Qt
from app.core import PushButton


class PaginationWidget(QWidget):
    """
    Pagination widget for displaying current number of items with possibility to change page with next, previous buttons.

    When pr, next buttons are clicked signal is sent with information about which page to load.
    Each page has 100 occurences.
    """

    page_changed = Signal(int)

    current_count_text = "Showing {count_from}-{count_to} of {total_count}"
    current_page_text = "Page {current_page} of {total_pages}"

    def __init__(
        self,
        current_page: int,
        total_pages: int,
        total_count: int,
        page_size: int = 100,
        parent=None,
    ):
        super().__init__(parent=parent)

        self.current_page = current_page
        self.total_pages = total_pages
        self.total_count = total_count
        self.page_size = page_size

        self.widget_layout = QHBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 5, 0, 5)
        self.widget_layout.setSpacing(5)

        # Current count
        self.current_count_label = QLabel(self)
        self.current_count_label.setText(
            self.current_count_text.format(
                count_from=self.current_page * self.page_size - 99,
                count_to=self.current_page * self.page_size,
                total_count=self.total_count,
            )
        )

        # Navigation buttons
        self.go_first_btn = PushButton(
            text="<< First",
            width=90,
            height=25,
            font_size=9,
            on_click=self._on_first_page_click,
        )
        self.go_previous_btn = PushButton(
            text="< Prev",
            width=90,
            height=25,
            font_size=9,
            on_click=self._on_prev_page_click,
        )

        self.current_page_label = QLabel(self)
        self.current_page_label.setText(
            self.current_page_text.format(
                current_page=self.current_page, total_pages=self.total_pages
            )
        )
        self.current_page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_page_label.setFixedWidth(110)

        self.go_next_btn = PushButton(
            text="Next >",
            width=90,
            height=25,
            font_size=9,
            on_click=self._on_next_page_click,
        )
        self.go_last_btn = PushButton(
            text="Last >>",
            width=90,
            height=25,
            font_size=9,
            on_click=self._on_last_page_click,
        )

        self.widget_layout.addWidget(self.current_count_label)
        self.widget_layout.addStretch()
        self.widget_layout.addWidget(self.go_first_btn)
        self.widget_layout.addWidget(self.go_previous_btn)
        self.widget_layout.addWidget(self.current_page_label)
        self.widget_layout.addWidget(self.go_next_btn)
        self.widget_layout.addWidget(self.go_last_btn)

    def _on_first_page_click(self):
        """On first page click - moves to first page"""
        if self.current_page > 1:
            self.page_changed.emit(1)

    def _on_prev_page_click(self):
        """On previous page click - moves to page - 1 if page is higher than 1"""
        if self.current_page > 1:
            self.page_changed.emit(self.current_page - 1)

    def _on_next_page_click(self):
        """On next page click - moves to page + 1 if page is not last"""
        if self.current_page < self.total_pages:
            self.page_changed.emit(self.current_page + 1)

    def _on_last_page_click(self):
        """On last page click - moves to last page"""
        if self.current_page < self.total_pages:
            self.page_changed.emit(self.total_pages)

    def reload(self, current_page: int, total_pages: int, total_count: int):
        """Reload widget - update information displayed for user in number of pages and current count."""
        self.current_page = current_page
        self.total_pages = total_pages
        self.total_count = total_count

        count_from = (self.current_page - 1) * self.page_size + 1
        count_to = min(self.current_page * self.page_size, self.total_count)

        if self.total_count < self.page_size:
            count_from = 1
            count_to = self.total_count

        if self.total_count < count_to and self.current_page == self.total_pages:
            count_to = self.total_count

        if total_pages == 0:
            count_from = 0
            self.current_page = 0

        self.current_count_label.setText(
            self.current_count_text.format(
                count_from=count_from,
                count_to=count_to,
                total_count=self.total_count,
            )
        )

        self.current_page_label.setText(
            self.current_page_text.format(
                current_page=self.current_page, total_pages=self.total_pages
            )
        )

        self.go_first_btn.set_enabled(self.current_page > 1)
        self.go_previous_btn.set_enabled(self.current_page > 1)
        self.go_next_btn.set_enabled(self.current_page < self.total_pages)
        self.go_last_btn.set_enabled(self.current_page < self.total_pages)
