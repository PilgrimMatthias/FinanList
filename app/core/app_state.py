from PySide6.QtCore import QObject, Signal


class AppState(QObject):
    user_changed = Signal(int)  # emits user_id
    wallet_changed = Signal(int)  # emits wallet_id
    category_changed = Signal(int)  # emits wallet_id
    transaction_changed = Signal(int)  # emits wallet_id
    recurring_transaction_changed = Signal(int)  # emits wallet_id

    def __init__(self):
        super().__init__()
        self._active_user_id = None
        self._active_wallet_id = None

    # User states
    def set_active_user(self, user_id: int):
        self._active_user_id = user_id
        self.user_changed.emit(user_id)

    @property
    def active_user_id(self) -> int:
        return self._active_user_id

    # Wallet states
    def set_active_wallet(self, wallet_id: int):
        self._active_wallet_id = wallet_id
        self.wallet_changed.emit(wallet_id)

    @property
    def active_wallet_id(self) -> int:
        return self._active_wallet_id

    # Category states
    def emit_categories_change(self):
        self.category_changed.emit(self._active_wallet_id)

    # Transaction states
    def emit_transaction_change(self):
        self.transaction_changed.emit(self._active_wallet_id)

    # Recurring transaction states
    def emit_crecurring_transaction_change(self):
        self.recurring_transaction_changed.emit(self._active_wallet_id)
