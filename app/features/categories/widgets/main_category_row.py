from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
)

from app.database import Category
from app.core import ColorCircle, HLine, PushButton, ExpandToggleButton
from .sub_category_row import SubCategoryRow


class MainCategoryRow(QWidget):
    # Main category signals
    sub_add_requested = Signal(Category)
    edit_requested = Signal(Category)
    delete_requested = Signal(Category)

    # Sub category signals
    sub_selection_changed = Signal()
    sub_edit_requested = Signal(Category)
    sub_delete_requested = Signal(Category)

    def __init__(self, category: Category, sub_categories: list[Category], parent=None):
        super().__init__(parent)

        self.category = category
        self.sub_categories = sub_categories

        self.sub_categories_rows = []

        self._init_view()

    def _init_view(self):

        # Main layout contentu
        main_cat_widget = QWidget()
        main_cat_layout = QHBoxLayout(main_cat_widget)
        main_cat_layout.setContentsMargins(0, 0, 0, 0)
        main_cat_layout.setSpacing(5)

        self.expand_btn = ExpandToggleButton(on_click=self._on_expand_click)

        self.color_circle = ColorCircle(parent=self, color=self.category.color, size=22)

        self.name_label = QLabel(self)
        self.name_label.setText(self.category.name)
        self.name_label.setObjectName("main_category_label")

        self.add_btn = PushButton(
            text="+",
            font_size=8,
            width=35,
            height=25,
            bg_color="#bfbfbf",
            bg_color_clicked="#a6a6a6",
            alternate_look=True,
            on_click=lambda: self.sub_add_requested.emit(self.category),
        )

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
        main_cat_layout.addWidget(self.expand_btn)
        main_cat_layout.addWidget(self.color_circle)
        main_cat_layout.addWidget(self.name_label)
        main_cat_layout.addStretch()
        main_cat_layout.addWidget(self.add_btn)
        main_cat_layout.addWidget(self.context_menu_btn)

        # Główny layout contentu
        self.sub_cat_widget = QWidget()
        self.sub_cat_layout = QVBoxLayout(self.sub_cat_widget)
        self.sub_cat_layout.setContentsMargins(10, 0, 0, 5)
        self.sub_cat_layout.setSpacing(5)

        self.set_subcategories(self.sub_categories)

        sep_line = HLine()
        sep_line.setContentsMargins(30, 0, 0, 0)

        # row layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 2, 0, 2)

        main_layout.addWidget(main_cat_widget)
        main_layout.addWidget(sep_line)
        main_layout.addWidget(self.sub_cat_widget)

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self._check_protected()
        self.sub_cat_widget.setVisible(False)

    def _check_protected(self):
        """Check if category is protected
        If yes than hide buttons
        """
        if self.category.is_protected:
            self.add_btn.hide()
            self.context_menu_btn.hide()

    def _on_context_menu(self):
        """Show QMenu with Edit/Delete/Add Sub options"""
        menu = QMenu(self)
        menu.addAction("Edit", lambda: self.edit_requested.emit(self.category))
        menu.addAction("Delete", lambda: self.delete_requested.emit(self.category))
        menu.exec(
            self.context_menu_btn.mapToGlobal(self.context_menu_btn.rect().bottomLeft())
        )

    def get_selectable_sub_rows(self) -> list[SubCategoryRow]:
        """Returns sub rows that can be selected (excludes protected)."""
        return [s for s in self.sub_categories_rows if not s.category.is_protected]

    def get_all_sub_rows(self) -> list[SubCategoryRow]:
        """Returns all sub rows including protected."""
        return list(self.sub_categories_rows)

    def set_subcategories(self, subs: list[Category]):
        """Create sub categories row"""
        self._clear_subs()
        self.sub_categories_rows = []
        for sub in subs:
            row = SubCategoryRow(sub)
            row.selection_changed.connect(self.sub_selection_changed.emit)
            row.edit_requested.connect(self.sub_edit_requested.emit)
            row.delete_requested.connect(self.sub_delete_requested.emit)

            self.sub_cat_layout.addWidget(row)
            self.sub_categories_rows.append(row)

    def _clear_subs(self):
        """Clear currently created sub categories"""
        while self.sub_cat_layout.count():
            item = self.sub_cat_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _on_expand_click(self):
        """On expand subs click
        Show/hide sub category rows
        """
        self.expand_btn.toggle()
        self.sub_cat_widget.setVisible(self.expand_btn.is_expanded())

    def set_selection_mode(self, enabled: bool):
        """Show or hide checkboxes on all sub rows."""
        for sub in self.sub_categories_rows:
            sub.set_selection_mode(enabled)

    def get_selected_category_ids(self) -> list[SubCategoryRow]:
        return [s.category.id for s in self.sub_categories_rows if s.is_checked()]
