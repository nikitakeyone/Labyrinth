from PyQt5 import QtGui, QtCore, QtWidgets

from grid import GridMatrix


class GridWidget(QtWidgets.QWidget):
    """Widget that displays a grid of walls."""

    def __init__(self, rows: int, columns: int, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.setMinimumSize(600, 600)
        self.grid = GridMatrix(rows, columns)

        self._grid_pixmap: QtGui.QPixmap = QtGui.QPixmap()
        self._grid_dirty = True

        self._square_size: float = 1.0
        self._canvas_width: int = 0
        self._canvas_height: int = 0
        self._canvas_left: int = 0
        self._canvas_top: int = 0
        self._update_layout()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """Handle widget resize events."""
        self._update_layout()
        super().resizeEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Paint the cached grid pixmap."""
        self._render_grid_pixmap()

        painter = QtGui.QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.drawPixmap(
            self._canvas_left,
            self._canvas_top,
            self._grid_pixmap,
        )

        super().paintEvent(event)

    def update_grid(self):
        """Call this when grid data changes to invalidate the cache."""
        self.invalidate_cache()
        self.update()

    def invalidate_cache(self):
        """Mark the grid cache as invalid."""
        self._grid_dirty = True

    def _update_layout(self):
        """
        Recalculate canvas size and position based on current widget size.
        """
        reference = self.width() * self.grid.rows / self.grid.columns
        if reference > self.height():
            self._square_size = (self.height() - 1) / self.grid.rows
        else:
            self._square_size = (self.width() - 1) / self.grid.columns

        self._canvas_width = round(self._square_size * self.grid.columns)
        self._canvas_height = round(self._square_size * self.grid.rows)
        self._canvas_left = round((self.width() - self._canvas_width) / 2)
        self._canvas_top = round((self.height() - self._canvas_height) / 2)
        self._grid_dirty = True

    def _render_grid_pixmap(self):
        """Render the grid to a pixmap for caching."""
        if not self._grid_dirty:
            return

        pixmap = QtGui.QPixmap(self._canvas_width, self._canvas_height)
        pixmap.fill(QtCore.Qt.transparent)

        painter = QtGui.QPainter(pixmap)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self._draw_grid_lines_cached(painter)
        self._draw_walls_cached(painter)

        painter.end()

        self._grid_pixmap = pixmap
        self._grid_dirty = False

    def _draw_grid_lines_cached(self, painter: QtGui.QPainter):
        """Draw grid lines on a cached pixmap."""
        painter.setOpacity(0.1)
        y = 0
        for _ in range(self.grid.rows + 1):
            painter.drawLine(0, int(y), self._canvas_width, int(y))
            y += self._square_size

        x = 0
        for _ in range(self.grid.columns + 1):
            painter.drawLine(int(x), 0, int(x), self._canvas_height)
            x += self._square_size

    def _draw_walls_cached(self, painter: QtGui.QPainter):
        """Draw walls on a cached pixmap."""
        wall_rect = QtCore.QRectF(0, 0, self._square_size, self._square_size)
        painter.setOpacity(1)
        painter.setBrush(QtGui.QColor(32, 32, 32))

        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                if self.grid.get_cell((row, column)):
                    x = column * self._square_size
                    y = row * self._square_size
                    painter.drawRect(wall_rect.translated(x, y))
