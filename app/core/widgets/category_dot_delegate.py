from PySide6.QtCore import Qt, QRect, QSize
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QStyledItemDelegate


class CategoryDotDelegate(QStyledItemDelegate):
    DOT_SIZE = 8
    LEFT_PADDING = 12
    GAP = 8
    RIGHT_PADDING = 8
    LINE_SPACING = 2
    MAX_LINES = 2
    OFF_COLOR = QColor("#808080")

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        data = index.data(Qt.UserRole)
        if not data:
            return

        is_active, color_hex, text = data
        text_x = option.rect.x() + self.LEFT_PADDING + self.DOT_SIZE + self.GAP
        available_width = option.rect.right() - text_x - self.RIGHT_PADDING

        lines = self._layout_text(text, available_width, painter.fontMetrics())

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        # Total content height (lines + spacing between)
        line_height = painter.fontMetrics().height()
        total_height = len(lines) * line_height + (len(lines) - 1) * self.LINE_SPACING

        # Vertically center the text block
        block_y = option.rect.y() + (option.rect.height() - total_height) // 2

        # Center the dot to the FIRST line, not the whole cell
        dot_y = block_y + (line_height - self.DOT_SIZE) // 2
        dot_rect = QRect(
            option.rect.x() + self.LEFT_PADDING,
            dot_y,
            self.DOT_SIZE,
            self.DOT_SIZE,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(color_hex) if is_active else self.OFF_COLOR)
        painter.drawEllipse(dot_rect)

        # Draw each line
        painter.setPen(QColor(option.palette.text().color()) if is_active else self.OFF_COLOR)
        for i, line in enumerate(lines):
            line_y = block_y + i * (line_height + self.LINE_SPACING)
            line_rect = QRect(text_x, line_y, available_width, line_height)
            painter.drawText(line_rect, Qt.AlignLeft | Qt.AlignVCenter, line)

        painter.restore()

    def sizeHint(self, option, index):
        data = index.data(Qt.UserRole)
        if not data:
            return super().sizeHint(option, index)

        color_hex, text = data
        available_width = (
            option.rect.width()
            - self.LEFT_PADDING
            - self.DOT_SIZE
            - self.GAP
            - self.RIGHT_PADDING
        )

        lines = self._layout_text(text, available_width, option.fontMetrics)
        line_height = option.fontMetrics.height()
        total_height = len(lines) * line_height + (len(lines) - 1) * self.LINE_SPACING

        return QSize(option.rect.width(), total_height + 16)  # +16 for vertical padding

    def _layout_text(self, text: str, available_width: int, metrics) -> list[str]:
        """Wraps text into at most MAX_LINES lines, truncating last with ellipsis if needed."""
        words = text.split()
        if not words:
            return [text]

        lines = []
        current_line = []

        for word in words:
            test = " ".join(current_line + [word]) if current_line else word
            if metrics.horizontalAdvance(test) <= available_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    # Single word longer than width — elide it
                    lines.append(
                        metrics.elidedText(word, Qt.ElideRight, available_width)
                    )
                    current_line = []

                if len(lines) >= self.MAX_LINES:
                    break

        # Add the last incomplete line if we have room
        if current_line and len(lines) < self.MAX_LINES:
            lines.append(" ".join(current_line))
            current_line = []

        # If words remain, truncate the last line
        words_used = sum(len(line.split()) for line in lines if "…" not in line)
        if words_used < len(words):
            last = lines[-1]
            ellipsis = "…"
            # Trim words from end until "last + …" fits
            while last and metrics.horizontalAdvance(last + ellipsis) > available_width:
                parts = last.rsplit(" ", 1)
                if len(parts) == 1:
                    last = metrics.elidedText(last, Qt.ElideRight, available_width)
                    break
                last = parts[0]
            lines[-1] = last + ellipsis

        return lines
