# core/widgets/dialogs.py (or wherever your show_error lives)
from PySide6.QtWidgets import QMessageBox


def show_confirmation(
    parent,
    message: str,
    title: str = "Confirm",
    confirm_text: str = "Yes",
    cancel_text: str = "Cancel",
) -> bool:
    """Show a confirmation dialog. Returns True if user confirmed."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)

    confirm_btn = msg_box.addButton(confirm_text, QMessageBox.AcceptRole)
    cancel_btn = msg_box.addButton(cancel_text, QMessageBox.RejectRole)
    msg_box.setDefaultButton(cancel_btn)

    msg_box.exec()

    return msg_box.clickedButton() == confirm_btn
