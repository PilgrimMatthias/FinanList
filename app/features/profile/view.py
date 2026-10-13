from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog
from app.core import show_error, PushButton, TextInput, HLine
from .service import ProfileService
from app.core.app_state import AppState
from app.core.utils import format_balance, cast_str_to_datetime
from app.core.exceptions import ValidationError

class ProfileView(QDialog):
    def __init__(self, profile_service: ProfileService, app_state: AppState,parent=None):
        super().__init__(parent)
        self.profile_service = profile_service
        self.app_state = app_state
        self.user = None
        self.user_profile = None
        self.profile_summary = None

        self.app_state.user_changed.connect(self._reload)

        self._init_view()

    def _init_view(self):
        self.setFixedSize(450,500)

        title_label = QLabel(self)
        title_label.setText("Profile")
        title_label.setObjectName("profileDialogTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel(self)
        subtitle_label.setText("Basic information used for estimates and forecasting")
        subtitle_label.setObjectName("profileDialogSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_hline = HLine()

        icon_widget = QWidget(self)
        icon_layout = QHBoxLayout(icon_widget)
        icon_layout.setSpacing(5)
        icon_layout.setContentsMargins(5, 5, 5, 5)

        self.profile_circle = QLabel(self)
        self.profile_circle.setText("N")
        self.profile_circle.setFixedSize(80, 80)
        self.profile_circle.setObjectName("profileDialogInitial")
        self.profile_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        name_widget = QWidget(self)
        name_layout = QVBoxLayout(name_widget)
        name_layout.setSpacing(5)
        name_layout.setContentsMargins(5, 5, 5, 5)
        
        self.name_label = QLabel(self)
        self.name_label.setObjectName("profileDialogNameLabel")
        self.name_label.setText("Name")
        self.name_label.setFixedWidth(120)

        self.member_label = QLabel(self)
        self.member_label.setText("Member since 1 January 1990")
        self.member_label.setObjectName("profileDialogMemberLabel")

        name_layout.addWidget(self.name_label)
        name_layout.addWidget(self.member_label)

        icon_layout.addWidget(self.profile_circle)
        icon_layout.addWidget(name_widget)
        icon_layout.addStretch()

        
        self.name_edit = TextInput(
            self,
            text = "Name",
            default_text="Name"
        )
        self.name_edit.text_input.textEdited.connect(self._check_user_changes)
        self.name_edit.text_input.textEdited.connect(self._update_name)

        salary_widget = QWidget(self)
        salary_layout = QHBoxLayout(salary_widget)
        salary_layout.setSpacing(5)
        salary_layout.setContentsMargins(0,0,0,0)
        
        self.net_salary_edit = TextInput(
            self,
            text = "Net Salary",
            sub_text="monthly",
            default_text="10000",
            validate_number=True
        )
        self.net_salary_edit.text_input.textEdited.connect(self._update_summary)
        self.net_salary_edit.text_input.textEdited.connect(self._check_user_changes)

        self.gross_salary_edit = TextInput(
            self,
            text = "Gross Salary",
            sub_text="monthly",
            default_text="10000",
            validate_number=True
        )
        self.gross_salary_edit.text_input.textEdited.connect(self._check_gross_salary)
        self.gross_salary_edit.text_input.textEdited.connect(self._check_user_changes)

        salary_layout.addWidget(self.net_salary_edit)
        salary_layout.addWidget(self.gross_salary_edit)
        
        self.expenses_edit = TextInput(
            self,
            text = "Estimated expenses",
            sub_text="monthly, used for forecasting",
            default_text="10000",
            error_text="Gross salary is usually higher than net salary",
            validate_number=True
        )
        self.expenses_edit.toggle_error(False)
        self.expenses_edit.text_input.textEdited.connect(self._update_summary)
        self.expenses_edit.text_input.textEdited.connect(self._check_user_changes)

        summary_widget = QWidget(self)
        summary_widget.setObjectName("profileSummary")
        summary_layout = QHBoxLayout(summary_widget)
        summary_layout.setSpacing(5)
        summary_layout.setContentsMargins(10,10,10,10)


        left_month_widget = QWidget(self)
        left_month_layout = QVBoxLayout(left_month_widget)
        left_month_layout.setSpacing(5)
        left_month_layout.setContentsMargins(0,0,0,0)

        left_title = QLabel(self)
        left_title.setText("Left each month")
        left_title.setObjectName("leftMonthTitle")

        self.left_amount = QLabel(self)
        self.left_amount.setText("+ 0 000,00 PLN")
        self.left_amount.setObjectName("leftMonthAmount")

        left_month_layout.addWidget(left_title)
        left_month_layout.addWidget(self.left_amount)

        savings_rate_widget = QWidget(self)
        savings_rate_layout = QVBoxLayout(savings_rate_widget)
        savings_rate_layout.setSpacing(5)
        savings_rate_layout.setContentsMargins(0,0,0,0)

        savings_title = QLabel(self)
        savings_title.setText("Savings rate")
        savings_title.setObjectName("savingsRateLabel")

        self.savings_rate_amount = QLabel(self)
        self.savings_rate_amount.setText("38,8 %")
        self.savings_rate_amount.setObjectName("savingsRateAmount")

        savings_rate_layout.addWidget(savings_title)
        savings_rate_layout.addWidget(self.savings_rate_amount)

        summary_layout.addWidget(left_month_widget)
        summary_layout.addWidget(savings_rate_widget)

        bottom_hline = HLine()

        button_widget = QWidget(self)
        button_layout = QHBoxLayout(button_widget)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(0,0,0,0)

        self.changes_label = QLabel(self)
        self.changes_label.setText("Unsaved changes")
        self.changes_label.setObjectName("profileUnsaved")
        self.changes_label.hide()

        cancel_btn = PushButton(
            text = "Cancel",
            width=80,
            height=30,
            font_size=10,
            object_name="dangerButton",
            on_click=lambda: self.close()
        )
        save_btn = PushButton(
            text = "Save",
            width=80,
            height=30,
            font_size=10,
            object_name="primaryButton",
            on_click=self._save_profile
        )

        button_layout.addWidget(self.changes_label)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)


        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Add widgets
        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(top_hline)
        main_layout.addWidget(icon_widget)
        main_layout.addWidget(self.name_edit)
        main_layout.addWidget(salary_widget)
        main_layout.addWidget(self.expenses_edit)
        main_layout.addWidget(summary_widget)
        main_layout.addWidget(bottom_hline)
        main_layout.addWidget(button_widget)

    def _reload(self, user_id:int = None):
        """Reload UI"""
        user_id = user_id or self.app_state.active_user_id
        if user_id is None:
            return
        
        self.user = self.profile_service.get_user(user_id=user_id)
        self.user_profile = self.profile_service.get_user_profile(user_id=user_id)
        self.profile_summary = self.profile_service.calculate_summary(
            net=self.user_profile.net_salary_monthly,
            expenses=self.user_profile.estimated_expenses_monthly
        )

        self.profile_circle.setText(self.user.name[0] if self.user.name else "?")
        self.name_edit.text_input.setText(self.user.name)
        self.name_label.setText(self.user.name)

        created_at = cast_str_to_datetime(
            self.user.created_at,
            "%Y-%m-%d %H:%M:%S"
        )
        self.member_label.setText(f"Member since {created_at.strftime("%d %B %Y")}")
        
        self.net_salary_edit.text_input.setText(format_balance(self.user_profile.net_salary_monthly))
        self.gross_salary_edit.text_input.setText(format_balance(self.user_profile.gross_salary_monthly))
        self.expenses_edit.text_input.setText(format_balance(self.user_profile.estimated_expenses_monthly))

        sign = "+" if self.profile_summary.left_each_month >= 0 else "-"
        self.left_amount.setText(f"{sign}{format_balance(abs(self.profile_summary.left_each_month))} {self.user_profile.currency.name}")

        self.savings_rate_amount.setText(f"{format_balance(self.profile_summary.savings_rate * 100)}%")

        positive = "true" if self.profile_summary.left_each_month >= 0 else "false"
        for label in (self.left_amount, self.savings_rate_amount):
            label.setProperty("positive", positive)
            label.style().unpolish(label)
            label.style().polish(label)

    def showEvent(self, event):
        """Override show with reload mechanism"""
        super().showEvent(event)
        self._reload()

    def _update_name(self):
        """Updates name label and profile initial"""
        name = self.name_edit.get_value()
        self.name_label.setText(str(name).capitalize())
        self.profile_circle.setText(str(name)[0].upper() if self.user.name else "?")

    def _update_summary(self):
        """Updates summary widget - live recompute"""
        if self.user_profile is None:
            return
    
        net = self.net_salary_edit.get_value()
        expenses = self.expenses_edit.get_value()
        self.profile_summary = self.profile_service.calculate_summary(
            net = net,
            expenses = expenses
        )
        sign = "+" if self.profile_summary.left_each_month >= 0 else "-"
        self.left_amount.setText(f"{sign}{format_balance(abs(self.profile_summary.left_each_month))} {self.user_profile.currency.name}")

        self.savings_rate_amount.setText(f"{format_balance(self.profile_summary.savings_rate * 100)}%")

        positive = "true" if self.profile_summary.left_each_month >= 0 else "false"
        for label in (self.left_amount, self.savings_rate_amount):
            label.setProperty("positive", positive)
            label.style().unpolish(label)
            label.style().polish(label)
        
    def _check_gross_salary(self):
        """Check if gross salary is lower than net salary"""
        gross_salary = self.gross_salary_edit.get_value()
        net_salary = self.net_salary_edit.get_value()

        self.expenses_edit.toggle_error(enabled=gross_salary < net_salary)

    def _check_user_changes(self):
        """Checks user changes to all fields"""
        if self.user is None or self.user_profile is None:
            return
        
        name = self.name_edit.get_value()
        gross_salary = self.gross_salary_edit.get_value()
        net_salary = self.net_salary_edit.get_value()
        expenses = self.expenses_edit.get_value()

        changes = False
        if name != self.user.name:
            changes = True
        if gross_salary != self.user_profile.gross_salary_monthly:
            changes = True
        if net_salary != self.user_profile.net_salary_monthly:
            changes = True
        if expenses != self.user_profile.estimated_expenses_monthly:
            changes = True

        self.changes_label.setVisible(changes)

    
    def _save_profile(self):
        """Saves user changes to profile"""
        self._update_name()

        name = self.name_edit.get_value()
        gross_salary = self.gross_salary_edit.get_value()
        net_salary = self.net_salary_edit.get_value()
        expenses = self.expenses_edit.get_value()

        try:
            self.profile_service.update_profile(
                user_id = self.user.id,
                name = name,
                net = net_salary,
                gross = gross_salary,
                expenses = expenses,
                currency = self.user_profile.currency.name
            )
            
            self._reload()
        except ValidationError as e:
            show_error(self, str(e))

        self._check_user_changes()

        
