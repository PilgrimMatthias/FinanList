from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget, QSizePolicy


class BarTrack(QFrame):
    """Horizontal proportional bar.

    The fill width is held by layout stretch factors rather than pixels, so the
    proportion survives window resizes without a resizeEvent handler.
    """

    PRECISION = 1000  # stretch resolution; 1000 => 0.1% steps

    def __init__(self, share: float = 0.0, color: str = "#808080", height: int = 7, parent=None):
        super().__init__(parent)
        self.setObjectName("barTrack")
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.fill = QFrame(self)
        self.fill.setObjectName("barFill")
        self.fill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Empty spacer
        self.spacer = QWidget(self)
        self.spacer.setObjectName("barSpacer")
        self.spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.fill)
        layout.addWidget(self.spacer)

        self._layout = layout
        self.set_data(share=share, color=color)

    def set_data(self, share: float, color: str = None):
        """share: 0.0-1.0. Values outside the range are clamped."""
        share = max(0.0, min(1.0, share or 0.0))

        filled = int(round(share * self.PRECISION))
        self._layout.setStretch(0, filled)
        self._layout.setStretch(1, self.PRECISION - filled)

        # A zero-stretch widget can still claim its minimum width, which would show a stub of colour at 0%. Hide it instead.
        self.fill.setVisible(filled > 0)

        if color:
            self.fill.setStyleSheet(
                f"QFrame#barFill {{ background-color: {color}; border-radius: {self.height() // 2}px; }}"
            )