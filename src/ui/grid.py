import typing as t

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from grid import GridMatrix


class WallGridWidget(QtWidgets.QWidget):
    """Base widget for drawing a grid with walls."""

    def __init__(self, rows: int, columns: int, *args, **kwargs):
        """."""
        super().__init__(*args, **kwargs)
        self.setMinimumSize(600, 600)
        self.grid = GridMatrix(rows, columns)
        self.square_size: float = 1.0
        self.set_square_size()

    def set_square_size(self):
        """
        Calculate and set the size of each cell based on widget dimensions.
        """
        reference = self.width() * self.grid.rows / self.grid.columns

        if reference > self.height():
            self.square_size = (self.height() - 1) / self.grid.rows
        else:
            self.square_size = (self.width() - 1) / self.grid.columns

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """Handle widget resize events."""
        self.set_square_size()
        super().resizeEvent(event)

    def get_canvas_size(self) -> t.Tuple[int, int]:
        """Get the size of the canvas area in pixels."""
        width = round(self.square_size * self.grid.columns)
        height = round(self.square_size * self.grid.rows)

        return width, height

    def get_canvas_origin(self) -> t.Tuple[int, int]:
        """Get the top-left corner of the canvas area."""
        width, height = self.get_canvas_size()

        left = round((self.width() - width) / 2)
        top = round((self.height() - height) / 2)

        return left, top

    def _draw_walls(self, qpainter: QtGui.QPainter):
        """Draw the walls in the grid."""
        left, top = self.get_canvas_origin()

        rectangle = QtCore.QRectF(0, 0, self.square_size, self.square_size)

        qpainter.setOpacity(1)
        qpainter.setBrush(QtGui.QColor(32, 32, 32))
        for row in range(self.grid.rows):
            for column in range(self.grid.columns):
                if self.grid.get_cell((row, column)):
                    # Упрощённый вызов translated
                    rect = rectangle.translated(
                        left + column * self.square_size,
                        top + row * self.square_size,
                    )
                    qpainter.drawRect(rect)

    def _draw_scene(self, qpainter: QtGui.QPainter):
        """Draw the grid lines."""
        width, height = self.get_canvas_size()
        left, top = self.get_canvas_origin()

        qpainter.setOpacity(0.1)
        y = top
        for row in range(self.grid.rows + 1):
            qpainter.drawLine(left, int(y), left + width, int(y))
            y += self.square_size

        x = left
        for column in range(self.grid.columns + 1):
            qpainter.drawLine(int(x), top, int(x), top + height)
            x += self.square_size

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Paint the grid."""
        qpainter = QtGui.QPainter(self)
        qpainter.translate(.5, .5)
        qpainter.setRenderHints(qpainter.Antialiasing)

        self._draw_scene(qpainter)
        self._draw_walls(qpainter)
        super().paintEvent(event)
