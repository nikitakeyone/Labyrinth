import colorsys
import enum
import typing as t
from math import floor

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from algorithms import (
    PathFindingAlgorithm,
    AStarAlgorithm,
    SolveStep,
    SolveQueue,
)
from grid import Cell
from .grid import WallGridWidget


class SolverGridWidget(WallGridWidget):
    """Widget for pathfinding visualization."""

    TARGET_COLOR = QtGui.QColor(0, 0, 255)
    SOURCE_COLOR = QtGui.QColor(255, 0, 0)
    SELECTED_COLOR = QtGui.QColor(163, 190, 140)
    USED_COLOR = QtGui.QColor(128, 128, 128)

    class DrawMode(enum.Enum):
        walls = 1
        source = 2
        target = 3

    class State(enum.Enum):
        viewing = 1
        drawing = 2
        erasing = 3
        solving = 4
        solved = 5

    def __init__(self, rows: int, columns: int, *args, **kwargs):
        super().__init__(rows, columns, *args, **kwargs)
        self.target: Cell = (0, 0)
        self.source: Cell = (rows - 1, columns - 1)
        self.algorithm: PathFindingAlgorithm = AStarAlgorithm()

        self.draw_mode = SolverGridWidget.DrawMode.walls
        self.installEventFilter(self)

        self._interval = 100

        self._state = SolverGridWidget.State.viewing
        self._state_changed: t.List[t.Callable] = []

        self._solve_queue = SolveQueue()
        self._used: t.Set[Cell] = set()
        self._current_path: t.Dict[Cell, t.Optional[Cell]] = dict()
        self._current_cell: t.Optional[Cell] = None

        self._timer = QtCore.QTimer(
            self,
            timeout=self._dequeue_solve_step,
            interval=self._interval,
        )

    def set_algorithm(self, algorithm: PathFindingAlgorithm):
        """Set the pathfinding algorithm to use."""
        self.algorithm = algorithm

    def set_algorithm_solve_queue(self):
        """Initialize the solve queue for the current algorithm."""
        self._solve_queue = self.algorithm.get_solve_queue(
            grid=self.grid,
            source=self.source,
            target=self.target,
        )
        self._used = set()
        self._current_cell = None
        self._current_path = []

    def resize_grid(self, rows: int, columns: int):
        """Resize the grid and adjust source/target positions."""
        self.grid.try_resize(rows, columns)

        if (
                self.target[0] >= self.grid.rows
                or self.target[1] >= self.grid.columns
        ):
            self.target = (0, 0)
            self.grid.try_reset_cell(self.target)

        if (
                self.source[0] >= self.grid.rows
                or self.source[1] >= self.grid.columns
        ):
            self.source = (self.grid.rows - 1, self.grid.columns - 1)
            self.grid.try_reset_cell(self.source)

        self.set_square_size()
        self.update()

    def solve(self) -> t.List[Cell]:
        """Solve the pathfinding problem and return the path."""
        return self.algorithm.solve(self.grid, self.source, self.target)

    def add_state_callback(self, callback: t.Callable[[], None]):
        """Add a callback to be called when the state changes."""
        if callable(callback):
            self._state_changed.append(callback)

    @property
    def interval(self) -> int:
        """Get the animation interval."""
        return self._interval

    @interval.setter
    def interval(self, new_value: int):
        """Set the animation interval."""
        if self.state == SolverGridWidget.State.viewing:
            self._interval = new_value
            self._timer.deleteLater()
            self._timer = QtCore.QTimer(
                self,
                timeout=self._dequeue_solve_step,
                interval=self._interval,
            )

    @property
    def state_changed(self) -> t.List[t.Callable[[], None]]:
        """Get the list of state change callbacks."""
        return self._state_changed

    @state_changed.setter
    def state_changed(self, new_state_changed: t.List[t.Callable[[], None]]):
        """Set the list of state change callbacks."""
        for callback in new_state_changed:
            if callable(callback):
                self._state_changed.append(callback)

    @property
    def state(self) -> "SolverGridWidget.State":
        """Get the current state."""
        return self._state

    @state.setter
    def state(self, new_state: "SolverGridWidget.State"):
        """Set the current state."""
        old_state = self._state

        if old_state == SolverGridWidget.State.solving:
            if new_state == SolverGridWidget.State.solved:
                self._stop_solving()
            elif new_state == SolverGridWidget.State.viewing:
                self._stop_solving()
                self._state = new_state

        elif old_state == SolverGridWidget.State.solved:
            if new_state == SolverGridWidget.State.solving:
                self._start_solving()
            elif new_state == SolverGridWidget.State.viewing:
                self._state = new_state

        elif old_state == SolverGridWidget.State.viewing:
            if new_state == SolverGridWidget.State.solved:
                self._start_solving()
                self._stop_solving()
            elif new_state == SolverGridWidget.State.solving:
                self._start_solving()
            else:
                self._state = new_state

        else:
            if new_state == SolverGridWidget.State.solving:
                self._state = new_state

        for callback in self._state_changed:
            callback()

        if old_state != self._state:
            self.update()

    def _start_solving(self):
        """Start the solving animation."""
        self.set_algorithm_solve_queue()

        self._timer.start()
        self._state = SolverGridWidget.State.solving

    def _stop_solving(self):
        """Stop the solving animation."""
        self._timer.stop()
        self._state = SolverGridWidget.State.solved
        self.update()

    def _dequeue_solve_step(self):
        """Process the next step in the solving animation."""
        if self._solve_queue.is_empty():
            self.state = SolverGridWidget.State.solved
        else:
            step: SolveStep = self._solve_queue.dequeue()
            self._used.update(step.used)
            self._current_path = step.path
            self._current_cell = step.selected
            self.update()

    def _draw_source_and_target(self, painter: QtGui.QPainter):
        """Draw the source and target cells."""
        left, top = self.get_canvas_origin()
        rectangle = QtCore.QRectF(0, 0, self.square_size, self.square_size)

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget.TARGET_COLOR)
        painter.drawRect(rectangle.translated(
            left + self.target[1] * self.square_size,
            top + self.target[0] * self.square_size,
        ))

        painter.setBrush(SolverGridWidget.SOURCE_COLOR)
        painter.drawRect(rectangle.translated(
            left + self.source[1] * self.square_size,
            top + self.source[0] * self.square_size,
        ))

    def _draw_current_solve_step(self, painter: QtGui.QPainter):
        """Draw the current step of the solving process."""
        left, top = self.get_canvas_origin()

        rectangle = QtCore.QRectF(0, 0, self.square_size, self.square_size)

        painter.setOpacity(0.5)
        painter.setBrush(SolverGridWidget.USED_COLOR)

        for x, y in self._used:
            painter.drawRect(rectangle.translated(
                left + y * self.square_size,
                top + x * self.square_size,
            ))

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget.SELECTED_COLOR)

        if len(self._current_path) == 0 or self._current_cell is None:
            return

        reconstructed_path = self.algorithm.reconstruct_path(
            came_from=self._current_path,
            source=self.source,
            target=self._current_cell,
        )

        self._current_path = dict()
        self._current_cell = None

        color = SolverGridWidget.SELECTED_COLOR

        for node_idx in range(len(reconstructed_path)):
            if len(reconstructed_path) != 1:
                # Calculate color based on position in path
                hue = 2 / 3 * node_idx / (len(reconstructed_path) - 1)
                rgb_color = colorsys.hls_to_rgb(hue, 0.5, 1)
                r, g, b = (floor(255 * c) for c in rgb_color)
                color = QtGui.QColor(r, g, b)

            painter.setBrush(color)
            node = reconstructed_path[node_idx]
            painter.drawRect(rectangle.translated(
                left + node[1] * self.square_size,
                top + node[0] * self.square_size,
            ))

    def _draw_result(self, painter: QtGui.QPainter):
        """Draw the final result of the pathfinding."""
        left, top = self.get_canvas_origin()

        rectangle = QtCore.QRectF(0, 0, self.square_size, self.square_size)

        result = self.solve()

        if result:
            # Process any remaining steps in the queue to show 'used' cells
            while not self._solve_queue.is_empty():
                step = self._solve_queue.dequeue()
                self._used.update(step.used)

            painter.setOpacity(0.33)
            painter.setBrush(SolverGridWidget.USED_COLOR)

            for x, y in self._used:
                painter.drawRect(rectangle.translated(
                    left + y * self.square_size,
                    top + x * self.square_size,
                ))

            painter.setOpacity(1)
            painter.setBrush(SolverGridWidget.SELECTED_COLOR)
            color = SolverGridWidget.SELECTED_COLOR

            for node_idx in range(len(result)):
                if len(result) != 1:
                    hue = 2 / 3 * node_idx / (len(result) - 1)
                    rgb_color = colorsys.hls_to_rgb(hue, 0.5, 1)
                    r, g, b = (floor(255 * c) for c in rgb_color)
                    color = QtGui.QColor(r, g, b)

                painter.setBrush(color)
                node = result[node_idx]
                painter.drawRect(rectangle.translated(
                    left + node[1] * self.square_size,
                    top + node[0] * self.square_size,
                ))
        else:
            self.state = SolverGridWidget.State.viewing

            message_box = QtWidgets.QMessageBox()
            message_box.setIcon(QtWidgets.QMessageBox.Warning)
            message_box.setText("Cannot exit the maze!")
            message_box.setInformativeText(
                f"No path exists from point {self.source} "
                f"to {self.target}!"
            )
            message_box.setWindowTitle("Error!")
            message_box.exec()

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Paint the grid and visualization."""
        painter = QtGui.QPainter(self)
        painter.translate(.5, .5)
        painter.setRenderHints(painter.Antialiasing)

        self._draw_scene(painter)
        self._draw_walls(painter)
        self._draw_source_and_target(painter)

        if self.state == SolverGridWidget.State.solving:
            self._draw_current_solve_step(painter)
        elif self.state == SolverGridWidget.State.solved:
            self._draw_result(painter)

        super().paintEvent(event)
        painter.end()

    def eventFilter(
            self,
            source: QtWidgets.QWidget,
            event: QtCore.QEvent,
    ) -> bool:
        """Filter events to handle mouse state changes."""
        if self.state == SolverGridWidget.State.viewing:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                if event.button() == QtCore.Qt.LeftButton:
                    self._state = SolverGridWidget.State.drawing
                elif event.button() == QtCore.Qt.RightButton:
                    self._state = SolverGridWidget.State.erasing

        elif self.state in (
                SolverGridWidget.State.drawing,
                SolverGridWidget.State.erasing,
        ):
            if event.type() == QtCore.QEvent.MouseButtonRelease:
                self._state = SolverGridWidget.State.viewing

        return super().eventFilter(source, event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """Handle mouse movement for drawing/erasing."""
        left, top = self.get_canvas_origin()
        width, height = self.get_canvas_size()

        x = event.pos().x()
        y = event.pos().y()

        i = floor((x - left) / self.square_size)
        j = floor((y - top) / self.square_size)

        if (left <= x <= left + width) and (top <= y <= top + height):
            if self.draw_mode == SolverGridWidget.DrawMode.walls:
                if self.state == SolverGridWidget.State.drawing:
                    self.grid.try_set_cell((j, i))
                elif self.state == SolverGridWidget.State.erasing:
                    self.grid.try_reset_cell((j, i))

            elif self.draw_mode == SolverGridWidget.DrawMode.target:
                if self.state == SolverGridWidget.State.drawing:
                    if not self.grid.get_cell((j, i)):
                        self.target = (j, i)

            elif self.draw_mode == SolverGridWidget.DrawMode.source:
                if self.state == SolverGridWidget.State.drawing:
                    if not self.grid.get_cell((j, i)):
                        self.source = (j, i)

            self.update()

        super().mouseMoveEvent(event)
