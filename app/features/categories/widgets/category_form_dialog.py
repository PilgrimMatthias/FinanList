import copy
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QDialog,
)
from enum import Enum
from app.core import (
    RadioInput,
    Frame,
    TextInput,
    PushButton,
    ComboBox,
    HLine,
    ColorPicker,
    show_error,
)


from app.database import Category
from app.core.enums import OperationType
from app.config import CATEGORY_WINDOW_WIDTH, CATEGORY_WINDOW_HEIGHT
from ..service import CategoryService
from app.core.exceptions import AppError, ValidationError


class CategoryType(Enum):
    MAIN = "main"
    SUB = "sub"


class CategoryOperationType(Enum):
    ADD = "New category"
    EDIT = "Edit category"


class CategoryFormDialog(QDialog):
    def __init__(
        self,
        category: Category | None,
        service: CategoryService,
        operation_type: CategoryOperationType = CategoryOperationType.ADD,
        parent=None,
    ):
        super().__init__(parent)
        self.category = category
        self.service = service
        self.operation_type = operation_type

        self.main_categories = self.service.get_all_main_dialog_categories(
            wallet_id=self.service.app_state.active_wallet_id
        )

        self._init_view()

    def _init_view(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFixedWidth(CATEGORY_WINDOW_WIDTH)
        self.setFixedHeight(CATEGORY_WINDOW_HEIGHT)

        # Główny layout contentu
        self.content = QWidget()
        self.content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(5, 10, 5, 10)
        self.content_layout.setSpacing(5)

        # Title
        self.title_label = QLabel(self)
        self.title_label.setText(self.operation_type.value)
        self.title_label.setObjectName("transactionLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        inputs_frame = Frame(self, add_stylesheet=False)
        input_layout = QVBoxLayout(inputs_frame)
        input_layout.setSpacing(0)
        input_layout.setContentsMargins(0, 0, 0, 0)

        # Type
        self.radio_input = RadioInput(
            text="Type",
            values=[
                (CategoryType.MAIN, "Main category"),
                (CategoryType.SUB, "Sub category"),
            ],
            default_value=self._set_category_type(),
            on_change=self._on_type_changed,
        )

        # Name
        self.name_input = TextInput(
            text="Name",
            placeholder="Enter category name",
            default_text=self._set_category_name(),
        )

        # Main category (only for sub)
        self.main_category_input = ComboBox(
            text="Main category",
            placeholder="Select main category",
            values=[(c.id, c.name) for c in self.main_categories],
            default_value=self._set_main_category(),
            on_change=self._on_main_category_changed,
        )

        # Default operation type
        self.operation_type_input = ComboBox(
            text="Default operation type",
            placeholder="Select operation type",
            values=[(operation.name, operation.value) for operation in OperationType],
            default_value=self._set_transaction_type(),
        )

        self.color_picker = ColorPicker(
            parent=self, text="Color", default_color=self._set_color()
        )

        input_layout.addWidget(self.radio_input)
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.main_category_input)
        input_layout.addWidget(self.operation_type_input)
        input_layout.addWidget(self.color_picker)

        # Button Frame
        button_frame = Frame(self, add_stylesheet=False)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0, 5, 0, 0)

        self.hline = HLine()

        self.cancel_btn = PushButton(
            text="Cancel",
            width=120,
            height=35,
            alternate_look=True,
            on_click=self.close,
        )

        self.create_btn = PushButton(
            text=(
                "Create" if self.operation_type == CategoryOperationType.ADD else "Save"
            ),
            width=120,
            height=35,
            on_click=self._on_create_edit_click,
        )

        button_layout.addWidget(self.cancel_btn, alignment=Qt.AlignmentFlag.AlignRight)
        button_layout.addWidget(self.create_btn, alignment=Qt.AlignmentFlag.AlignRight)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.content_layout.addWidget(self.title_label)
        self.content_layout.addWidget(inputs_frame)
        self.content_layout.addStretch()
        self.content_layout.addWidget(self.hline)
        self.content_layout.addWidget(button_frame)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(self.content)

        # Set alignment of widget
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._on_type_changed()

        if self.operation_type == CategoryOperationType.EDIT:
            self.radio_input.hide()

    # SET FORM VALUES
    def _set_category_type(self) -> CategoryType:
        """
        Sets category type
        For ADD:
            - Main if category is main
            - Sub otherwise
        For EDIT:
            - Main if category is main
            - Sub otherwise

        Returns:
            CategoryType: category type
        """
        match self.operation_type:
            case CategoryOperationType.ADD:
                # if self.category is not None and self.category.parent_id is not None:
                if self.category is None:
                    return CategoryType.MAIN
                else:
                    return CategoryType.SUB

            case CategoryOperationType.EDIT:
                # if self.category is not None and self.category.parent_id is None:
                if self.category.parent_id is None:
                    return CategoryType.MAIN
                return CategoryType.SUB

        return CategoryType.MAIN

    def _set_category_name(self) -> str | None:
        """
        Sets category name for EDIT operation

        Returns:
            str | None: category name
        """
        if (
            self.operation_type == CategoryOperationType.EDIT
            and self.category is not None
        ):
            return self.category.name

        return None

    def _set_main_category(self) -> str | None:
        """
        Sets main category name.
        For ADD:
            - main category name
        For EDIT:
            - main category name for sub

        Returns:
            str | None: main category name
        """
        if self.category is not None:
            match self.operation_type:
                case CategoryOperationType.ADD:
                    if self.category.parent_id is None:
                        return self.category.name

                case CategoryOperationType.EDIT:
                    if self.category.parent_id is not None:
                        return [
                            main.name
                            for main in self.main_categories
                            if main.id == self.category.parent_id
                        ][0]

        return None

    def _set_transaction_type(self) -> OperationType | None:
        """
        Sets category operation type.

        Returns:
            OperationType | None: operation type
        """
        if self.category is not None:
            return self.category.operation_type

        return None

    def _set_color(self) -> str | None:
        """
        Set color for provided category

        Returns:
            str | None: color from category
        """
        if self.category is not None:
            return self.category.color

        return None

    # WIDGET TRIGGERS
    def _on_type_changed(self):
        """On category type change
        Hides/shows main category input"""
        category_type = self.radio_input.get_value()
        if category_type == CategoryType.MAIN:
            self.main_category_input.hide()
        else:
            self.main_category_input.show()

    def _on_main_category_changed(self):
        """On main category changed
        Sets main operation type for main category if sub is currently created.
        """
        if self.main_category_input.isHidden():
            return

        main_category = [
            category
            for category in self.main_categories
            if category.id == self.main_category_input.get_data()
        ][0]
        category_type = self.radio_input.get_value()

        if category_type == CategoryType.SUB:
            self.operation_type_input.set_value(main_category.operation_type)

    def _on_create_edit_click(self):
        """Trigger for category add/edit"""
        match self.operation_type:
            case CategoryOperationType.ADD:
                self.create_category()
            case CategoryOperationType.EDIT:
                self.edit_category()

    # CATEGORY OPERATIONS
    def _show_error(self, msg: str):
        """Show error dialog"""
        show_error(self, message=msg)

    def _validate_inputs(self) -> bool:
        """Validation of user inputs"""
        # Validation
        msg = []

        # Validate inputs
        required_fields = {
            "type": self.radio_input,
            "name": self.name_input,
            "default operation type": self.operation_type_input,
            "color": self.color_picker,
        }
        if self.radio_input.get_value() == CategoryType.SUB:
            required_fields["main category"] = self.main_category_input

        msg = [name for name, field in required_fields.items() if not field.is_filled()]

        # Display error box if sth must be filled
        if len(msg) > 0:
            self._show_error(f"Please fill in: {', '.join(msg)}")
            return False

        return True

    def edit_category(self):
        """Edit category"""
        if not self._validate_inputs():
            return

        updated_category = copy.deepcopy(self.category)

        updated_category.name = self.name_input.get_value()
        updated_category.color = self.color_picker.get_color()

        updated_category.operation_type = self.operation_type_input.get_value()

        if self.radio_input.get_value() == CategoryType.SUB:
            parent_id = self.main_category_input.get_data()
            updated_category.parent_id = parent_id

        try:
            self.service.update_category(updated_category)
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")

    def create_category(self):
        """Create category"""
        # Validation
        if not self._validate_inputs():
            return

        wallet_id = self.service.app_state.active_wallet_id

        parent_id = None
        if self.radio_input.get_value() == CategoryType.SUB:
            parent_id = self.main_category_input.get_data()

        try:
            self.service.create_category(
                wallet_id=wallet_id,
                name=self.name_input.get_value(),
                color=self.color_picker.get_color(),
                parent_id=parent_id,
                operation_type=self.operation_type_input.get_value(),
            )
            self.close()
        except ValidationError as e:
            self._show_error(str(e))
        except AppError as e:
            self._show_error(f"Something went wrong: {e}")
