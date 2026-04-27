from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QMenu,
)

from app.database import Category
from app.core import ColorCircle, HLine, PushButton


class SubCategoryRow(QWidget):
    selection_changed = Signal()
    edit_requested = Signal(Category)
    delete_requested = Signal(Category)

    def __init__(self, category: Category, parent=None):
        super().__init__(parent)

        self.category = category

        self._init_view()

    def _init_view(self):
        # row layout
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(5)
        row_layout.setContentsMargins(0, 0, 0, 0)

        self.checkbox = QCheckBox()
        self.checkbox.toggled.connect(self._on_checkbox_toggled)
        self.checkbox.hide()

        self.color_circle = ColorCircle(parent=self, color=self.category.color, size=18)

        self.name_label = QLabel(self)
        self.name_label.setText(self.category.name)
        self.name_label.setObjectName("category_label")

        self.type_label = QLabel(self)
        self.type_label.setText(self.category.operation_type.value)
        self.type_label.setContentsMargins(2, 1, 2, 1)
        self.type_label.setObjectName(self.category.operation_type.value)

        self.context_menu_btn = PushButton(
            text="⋯",
            font_size=8,
            width=35,
            height=25,
            bg_color="#bfbfbf",
            bg_color_clicked="#a6a6a6",
            alternate_look=True,
            on_click=self._on_context_menu,
        )

        # Add widgets
        row_layout.addWidget(self.checkbox)
        row_layout.addWidget(self.color_circle)
        row_layout.addWidget(self.name_label)
        row_layout.addStretch()
        row_layout.addWidget(self.type_label)
        row_layout.addWidget(self.context_menu_btn)

        # Set alignment of widget
        row_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        hline = HLine()
        hline.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(30, 2, 0, 2)

        main_layout.addWidget(row_widget)
        main_layout.addWidget(hline)

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._check_protected()

    def _check_protected(self):
        """Check if category is protected
        If yes than hide buttons
        """
        if self.category.is_protected:
            self.context_menu_btn.hide()

    def _on_context_menu(self):
        """Show QMenu with Edit/Delete/Add Sub options"""
        menu = QMenu(self)
        menu.addAction("Edit", lambda: self.edit_requested.emit(self.category))
        menu.addAction("Delete", lambda: self.delete_requested.emit(self.category))
        menu.exec(
            self.context_menu_btn.mapToGlobal(self.context_menu_btn.rect().bottomLeft())
        )

    def _on_checkbox_toggled(self):
        """Emit signal on checkbox toggled"""
        self.selection_changed.emit()

    def set_selection_mode(self, enabled: bool):
        """Show or hide checkbox. Protected categories never show."""
        if self.category.is_protected:
            return

        self.checkbox.setVisible(enabled)
        self.context_menu_btn.setVisible(not enabled)

        if not enabled:
            self.checkbox.setChecked(False)

    def set_checked(self, check=True):
        """Set checked box state"""
        if not self.category.is_protected:
            self.checkbox.setChecked(check)

    def is_checked(self) -> bool:
        """Check if checkbox is checked"""
        return self.checkbox.isChecked()
