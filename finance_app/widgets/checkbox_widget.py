from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class CheckBoxWidget(QCheckBox):
    def __init__(
        self,
        parent=None,
        widget_text="",
        is_text_hidden=False,
        hidden_propert_name="id",
        checked=False,
        box_style="normal",
    ):
        super().__init__()
        self.widget_text = widget_text
        self.is_text_hidden = is_text_hidden
        self.hidden_propert_name = hidden_propert_name
        self.checked = checked
        self.box_style = box_style

        self.init_checkbox()

    def init_checkbox(self):
        """
        Check box initialization
        """
        match self.box_style:
            case "small":
                self.setStyleSheet(
                    """
                    QCheckBox::indicator{
                        width: 15px;
                        height: 15px;
                    }
                    QCheckBox{
                        border:0px;
                    }
                    """
                )
            case _:
                self.setStyleSheet(
                    """
                    QCheckBox::indicator{
                        width: 20px;
                        height: 20px;
                    }
                    QCheckBox{
                        border:0px;
                    }

                    """
                )

        self.setChecked(self.checked)

        if self.is_text_hidden:
            self.setProperty(self.hidden_propert_name, self.widget_text)
        else:
            self.setText(self.widget_text)

        self.stateChanged.connect(self.get_hidden_property)

    def get_hidden_property(self):
        """
        Get hidden property of checkbox
        """
        return self.property(self.hidden_propert_name)
