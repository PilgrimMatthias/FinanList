from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, QEvent
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QTableView, QAbstractItemView, QHeaderView

from app.core.theme.palette import Palette

CELL_PADDING = 8
TEXT_MARGIN = 10


class _FooterModel(QAbstractTableModel):
    """One row of already-formatted strings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._values: list[str] = []
        self._alignments: list[int] = []
        self._tones: list[str | None] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return 1 if self._values else 0

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self._values)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._values[index.column()]
        if role == Qt.TextAlignmentRole:
            return self._alignments[index.column()]
        if role == Qt.ForegroundRole:
            tone = self._tones[index.column()] if self._tones else None
            return Palette.color(tone or "text_primary")
        return None

    def set_values(self, values: list[str], alignments: list[int], tones=None):
        self.beginResetModel()
        self._values = values
        self._alignments = alignments
        self._tones = list(tones) if tones else []
        self.endResetModel()


class TableFooter(QTableView):
    """A pinned summary row under a table, aligned to its columns.

    self.footer = TableFooter(self)
    self.footer.follow(self.table)
    self.footer.set_values(model.footer_values())
    """

    def __init__(self, parent=None, height: int = 36):
        super().__init__(parent)

        self.setObjectName("tableFooter")
        self._model = _FooterModel(self)
        self.setModel(self._model)
        self._source = None
        self._scrollbar = None

        self.setFixedHeight(height)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setShowGrid(False)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def follow(self, table: QTableView):
        """Mirror another table's columns, and keep mirroring them."""
        self._source = table
        self._scrollbar = table.verticalScrollBar()

        # Without this the footer outlives the table during teardown and
        # its event filter calls into a deleted C++ object.
        table.destroyed.connect(self._on_source_destroyed)

        header = table.horizontalHeader()
        header.sectionResized.connect(self._sync_columns)
        header.sectionCountChanged.connect(lambda *_: self._sync_columns())

        # The source grows a scrollbar the moment its rows overflow, which
        # narrows its viewport and shifts every column left. Watching the
        # scrollbar's show/hide is the only signal Qt gives for that.
        self._scrollbar.installEventFilter(self)

        self._sync_columns()

    def set_values(
        self, values: list[str], alignments: list[int] = None, tones: list = None
    ):
        """Replace the row. Alignment defaults to left first, right rest.

        `tones` is one Palette key (or None for the default text colour)
        per cell, so a total can be green or red like the rows above it.
        """
        if alignments is None:
            left = int(Qt.AlignVCenter | Qt.AlignLeft)
            right = int(Qt.AlignVCenter | Qt.AlignRight)
            alignments = [left] + [right] * (len(values) - 1)

        self._model.set_values(values, alignments, tones)
        self._sync_columns()

    def eventFilter(self, watched, event):
        if watched is self._scrollbar and self._source is not None:
            if event.type() in (QEvent.Type.Show, QEvent.Type.Hide):
                self._sync_columns()
        return super().eventFilter(watched, event)

    def _on_source_destroyed(self, *args):
        self._source = None
        self._scrollbar = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._sync_columns()

    def _sync_columns(self, *args):
        """Copy column widths, then reserve the scrollbar's width."""
        if self._source is None:
            return

        header = self._source.horizontalHeader()
        columns = min(self._model.columnCount(), header.count())

        for column in range(columns):
            self.setColumnWidth(column, header.sectionSize(column))

        margin = (
            self._scrollbar.width()
            if self._scrollbar is not None and self._scrollbar.isVisible()
            else 0
        )
        self.setViewportMargins(0, 0, margin, 0)

    def content_width(self, column: int) -> int:
        """Width the footer's own text needs in `column`.

        The footer is bold and the rows above it are not, so a column the
        source table sized to its rows can be a few pixels too narrow for
        the total ("100,0%" -> "100,…").
        """
        if not (0 <= column < self._model.columnCount()):
            return 0
        text = self._model.data(self._model.index(0, column), Qt.DisplayRole) or ""
        if not text:
            return 0

        bold = QFont(self.font())
        bold.setWeight(QFont.Weight.DemiBold)
        return (
            QFontMetrics(bold).horizontalAdvance(text) + 2 * CELL_PADDING + TEXT_MARGIN
        )

    def set_column_hidden(self, column: int, hidden: bool):
        """Mirror a hidden column on the source table."""
        self.setColumnHidden(column, hidden)
        self._sync_columns()
