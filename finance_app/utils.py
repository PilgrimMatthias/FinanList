# Utils file with general methods

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication

from datetime import datetime


def center_window(
    self, width, height, fix_size=False, offset_x=0, offset_y=0, center=True
):
    """
    Method used for centering window on the screen.

    Parameters
        - width: width of the app window in pixels
        - height: height of the window in pixels
        - fix_size: optional parameter to make window fixed_size, default False
        - offset_x: number of pixels to position on horizontal view (left-right), default 0
        - offset_y: number of pixels to position on vertical view (top-bottom), default 0
        - center: optional parameter to resize window without centering it, default True

    """
    if fix_size:  # Opcja fix size dla login screen
        # Zmiana wielkości okna
        self.resize(width, height)

        # Ustawienie przycisków okna (Zamknięcię, minimalizacja)
        self.setWindowFlags(
            Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint
        )
    else:
        # Zmiana wielkości okna
        self.resize(width, height)

        # Ustawienie przycisków okna (Zamknięcię, minimalizacja, maksymalizacja)
        self.setWindowFlags(
            Qt.Window
            | Qt.WindowCloseButtonHint
            | Qt.WindowMaximizeButtonHint
            | Qt.WindowMinimizeButtonHint
        )
        # Przeładowanie okna
        self.show()

    # Wycentrowanie okna
    if center:
        frame_gm = self.frameGeometry()
        screen = QApplication.primaryScreen()
        center_point = screen.availableGeometry().center()
        center_point += QPoint(offset_x, offset_y)
        frame_gm.moveCenter(center_point)
        self.move(frame_gm.topLeft())


def filter_func(pair, condition):
    """
    Methos used for returning boolean value for dict values comparison.

    Args:
        pair (dict): pair of values from dict
        condition (dict): dict for comparison

    Returns:
        bollean: information if pair is equel to condition
    """
    if list(pair.values()) == condition:
        return True
    return False


def is_number(value):
    """
    Verification if value is number

    Args:
        number (str): value

    Returns:
        _type_: boolean
    """
    try:
        float(value.replace(",", "."))
    except ValueError:
        return False

    return True


def is_date(value, format):
    """
    Verification if value is date

    Args:
        number (str): value

    Returns:
        _type_: boolean
    """
    try:
        datetime.strptime(value, format)
    except:
        return False

    return True
