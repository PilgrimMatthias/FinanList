from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)
from app.core import Frame, PushButton, show_error, show_confirmation

from app.database.models import Category
from .widgets.category_form_dialog import CategoryFormDialog, CategoryOperationType
from .widgets.main_category_row import MainCategoryRow
from .widgets.sub_category_row import SubCategoryRow
from .service import CategoryService
from app.core.app_state import AppState
from app.core.exceptions import ValidationError


class CategoriesView(QWidget):
    def __init__(self, service: CategoryService, app_state: AppState, parent=None):
        super().__init__(parent=parent)
        self.service = service
        self.app_state = app_state
        self._is_selection_mode = False
        self._main_rows = []

        self._init_view()

        self.app_state.wallet_changed.connect(self._reload)
        self.app_state.category_changed.connect(self._on_category_change)

    def _init_view(self):
        """Initialize view"""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumWidth(0)

        # Top Buttons frame
        top_btn_frame = Frame(self, add_stylesheet=False)
        top_btn_layout = QHBoxLayout(top_btn_frame)
        top_btn_layout.setSpacing(5)
        top_btn_layout.setContentsMargins(0, 0, 0, 10)

        self.select_btn = PushButton(
            text="Select",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_select_categories,
        )

        self.select_all_btn = PushButton(
            text="Select all",
            alternate_look=True,
            width=100,
            height=30,
            font_size=9,
            on_click=self._on_select_all_clicked,
        )
        self.select_all_btn.hide()

        self.delete_btn = PushButton(
            text="Delete selected",
            bg_color="#ff9999",
            bg_color_clicked="#ff3333",
            font_size=9,
            width=150,
            height=30,
            on_click=self._on_delete_selected,
        )
        self.delete_btn.hide()

        self.create_category = PushButton(
            text="+ Add Category",
            on_click=lambda: self._on_add_category(category=None),
            font_size=9,
            width=150,
            height=30,
        )

        top_btn_layout.addWidget(self.select_btn)
        top_btn_layout.addWidget(self.select_all_btn)
        top_btn_layout.addStretch()
        top_btn_layout.addWidget(self.delete_btn)
        top_btn_layout.addWidget(self.create_category)

        # Categories frame
        categories_frame = Frame(self, add_stylesheet=False)
        self.categories_layout = QVBoxLayout(categories_frame)
        self.categories_layout.setSpacing(0)
        self.categories_layout.setContentsMargins(0, 0, 0, 0)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(top_btn_frame)
        main_layout.addWidget(categories_frame)
        main_layout.addStretch()

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    # VIEW UPDATE
    def _on_category_change(self, wallet_id):
        """On category method to reload view"""
        # Only reload if the change was for our current wallet
        if wallet_id == self.app_state.active_wallet_id:
            self._reload(wallet_id)

    def _reload(self, wallet_id: int):
        """Method to reload all categories in view - recreates them"""
        if wallet_id is None:
            self._clear()
            return

        self._exit_selection_mode()
        self._clear()
        main_categories = self.service.get_all_main_categories(wallet_id)

        self._main_rows = []
        for main_cat in main_categories:
            main_widget = self._build_category_row(main=main_cat)
            self._main_rows.append(main_widget)
            self.categories_layout.addWidget(main_widget)

    def _clear(self):
        """Remove all category rows from the list."""
        while self.categories_layout.count():
            item = self.categories_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _exit_selection_mode(self):
        if self._is_selection_mode:
            self._is_selection_mode = False
            self.select_btn.setText("Select")
            self.create_category.show()
            self.delete_btn.hide()
            self.select_all_btn.hide()

        for main_cat in self._main_rows:
            main_cat.set_selection_mode(False)

    def _build_category_row(self, main: Category) -> MainCategoryRow:
        """Method to build main category row and connect all the signals"""
        subs = self.service.get_all_subcategories(main.id)
        main_row = MainCategoryRow(category=main, sub_categories=subs)
        main_row.sub_selection_changed.connect(self._update_buttons)

        # Signals connected to main category change
        main_row.sub_add_requested.connect(self._on_add_category)
        main_row.edit_requested.connect(self._edit_category)
        main_row.delete_requested.connect(self._delete_category)

        # Signals connected to sub category changed
        main_row.sub_edit_requested.connect(self._edit_category)
        main_row.sub_delete_requested.connect(self._delete_category)
        return main_row

    # BUTTON OPERATIONS
    def _update_buttons(self):
        """Method to invoke button updates"""
        self._update_delete_button()
        self._update_select_all_button()

    def _get_all_selectable_sub_rows(self) -> list[SubCategoryRow]:
        """All sub rows currently in the UI. Protected rows excluded."""
        rows = []
        for main_row in self._main_rows:
            for sub_row in main_row.get_selectable_sub_rows():
                rows.append(sub_row)
        return rows

    def _update_select_all_button(self):
        """Method to update select all button
        If all transactions are checked then it changes name to Deselect all.
        If just one is not checked than name is changed to Select all.
        """
        rows = self._get_all_selectable_sub_rows()
        if not rows:
            self.select_all_btn.setEnabled(False)
            return

        self.select_all_btn.setEnabled(True)
        all_selected = all(r.is_checked() for r in rows)
        self.select_all_btn.setText("Deselect all" if all_selected else "Select all")

    def _update_delete_button(self):
        """Update delete selected button
        If number of checked buttons is more than 1 than name is set to Delecte selected ([count]).
        If count is 0 than button is disabled and name is set to Delete selected.
        """
        rows = self._get_all_selectable_sub_rows()
        count = sum(1 for r in rows if r.is_checked())

        if count == 0:
            self.delete_btn.setEnabled(False)
            self.delete_btn.setText("Delete selected")
        else:
            self.delete_btn.setEnabled(True)
            self.delete_btn.setText(f"Delete selected ({count})")

    def _on_select_all_clicked(self):
        """Trigger for on select/deselect all button
        Toggles all sub rows in main row.
        """
        selectable_rows = self._get_all_selectable_sub_rows()
        all_selected = all(r.is_checked() for r in selectable_rows)

        # Toggle: if all selected, deselect all. Otherwise select all.
        for row in selectable_rows:
            row.set_checked(not all_selected)

        self._update_buttons()

    def _on_select_categories(self):
        """Trigger on select button clicked
        Hides/shows buttons
        """
        self._is_selection_mode = not self._is_selection_mode

        if self._is_selection_mode:
            self.select_btn.setText("Cancel")
            self.create_category.hide()
            self.delete_btn.show()
            self.select_all_btn.show()
        else:
            self.select_btn.setText("Select")
            self.create_category.show()
            self.delete_btn.hide()
            self.select_all_btn.hide()

        for main_cat in self._main_rows:
            main_cat.set_selection_mode(self._is_selection_mode)

        self._update_buttons()

    # CATEGORY OPERATIONS
    def _on_add_category(self, category: Category | None = None):
        """On add category signal trigger - creates form dialog"""
        dialog = CategoryFormDialog(category, self.service, parent=self)
        dialog.show()

    def _edit_category(self, category: Category):
        """On edit category signal triggered"""
        dialog = CategoryFormDialog(
            category=category,
            service=self.service,
            operation_type=CategoryOperationType.EDIT,
            parent=self,
        )
        dialog.show()

    def _delete_category(self, category: Category):
        """On delete category signal triggerd"""

        count = self.service.get_affected_transaction_count([category.id])
        if category.parent_id is None:
            # Main category — warn about subcategories too
            sub_count = len(self.service.get_all_subcategories(category.id))
            message = (
                f"This will delete '{category.name}' and {sub_count} subcategories.\n\n"
                f"{count} transactions will be reassigned to Uncategorized.\n\n"
                f"Continue?"
            )
        else:
            message = (
                f"This will delete '{category.name}'.\n\n"
                f"{count} transactions will be reassigned to Uncategorized.\n\n"
                f"Continue?"
            )

        if show_confirmation(
            self, message, title="Delete category", confirm_text="Delete"
        ):
            try:
                self.service.delete_categories([category.id])
                self._update_buttons()
            except ValidationError as e:
                show_error(self, str(e))

    def _on_delete_selected(self):
        """On delete selected signal triggered
        Deletes categories that are checked
        """
        subs_to_delete = []
        for main in self._main_rows:
            subs_to_delete += main.get_selected_category_ids()

        if not subs_to_delete:
            return

        count = self.service.get_affected_transaction_count(subs_to_delete)
        message = (
            f"Delete {len(subs_to_delete)} categories?\n\n"
            f"{count} transactions will be reassigned to Uncategorized."
        )
        if show_confirmation(
            self, message, title="Delete categories", confirm_text="Delete"
        ):
            try:
                self.service.delete_categories(subs_to_delete)

                self._exit_selection_mode()
            except ValidationError as e:
                show_error(self, str(e))
