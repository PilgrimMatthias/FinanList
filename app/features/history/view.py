from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout


# Placeholder — just enough to test sidebar switching
class HistoryView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("History - TODO"))
