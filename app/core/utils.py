# Utils file with general methods

from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QApplication

from datetime import datetime
from dateutil.relativedelta import relativedelta

from .enums import RecurrenceInterval


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
        float(value.replace(" ", "").replace(",", "."))
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


def set_next_due_date(start_date: datetime, interval: RecurrenceInterval) -> datetime:
    """sets next due date"""
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    next_due_date = now

    if start_date <= now.date():
        match interval:
            case RecurrenceInterval.DAILY:
                next_due_date += relativedelta(days=1)
            case RecurrenceInterval.WEEKLY:
                next_due_date += relativedelta(weeks=1)
            case RecurrenceInterval.MONTHLY:
                next_due_date += relativedelta(months=1, day = start_date.day)
            case RecurrenceInterval.YEARLY:
                next_due_date += relativedelta(years=1, day = start_date.day, month = start_date.month)

        return next_due_date.strftime(format="%Y-%m-%d")

    return start_date

def cast_datetime_to_str(date: datetime, format: str = "%d.%m.%Y"):
    """Casts datetime date to string with proper format"""
    try:
        return date.strftime(format)
    except Exception as e:
        print("Error during convert to string from datetime", e)


def cast_date_to_proper_format(date: str, format: str = "%d.%m.%Y"):
    "Casts date as string to datetime"
    # new_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    new_date = datetime.strptime(date, "%Y-%m-%d")

    return new_date.strftime(format=format)


# def cast_str_to_datetime(date: datetime, format="%Y-%m-%d %H:%M:%S"):
def cast_str_to_datetime(date: str, format="%Y-%m-%d"):
    """Casts string to datetime"""
    try:
        new_date = datetime.strptime(date, format)

        return new_date
    except Exception as e:
        return date
