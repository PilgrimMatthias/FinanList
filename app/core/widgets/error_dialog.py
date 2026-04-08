from PySide6.QtWidgets import QMessageBox


def show_error(parent, message: str, title: str = "Error"):
    """
    Show error dialog

    Args:
        message (str): message for error box
        title (str, optional): title for error box. Defaults to "Error".
    """
    QMessageBox.warning(parent, title, message)
