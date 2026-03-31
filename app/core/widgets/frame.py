from PySide6.QtWidgets import (
    QSizePolicy,
    QFrame,
)


class Frame(QFrame):
    """
    Customowy QFrame wykorzystywany pod opakowanie zbioru widżetów w ramkę.
    """

    def __init__(
        self, parent=None, min_width=None, max_width=None, add_stylesheet=True
    ):
        super().__init__()

        self.setObjectName("btn_frame")

        if add_stylesheet:
            self.setStyleSheet(
                """
                    QFrame#btn_frame {
                        border: 2px solid #a6a6a6;
                        border-radius: 8px;
                        background-color: #FFFFFF;
                    }
            """
            )

        if max_width is not None:
            self.setMaximumWidth(max_width)

        if min_width is not None:
            self.setMinimumWidth(min_width)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
