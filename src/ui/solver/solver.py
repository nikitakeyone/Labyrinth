import colorsys
import typing as t
from math import floor

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets

from algorithms import PathFindingAlgorithm, AStarAlgorithm, SolveStep
from grid import Cell
from .grid import GridWidget
from .model import SolverModel, DrawMode
from .state import (
    SolverStateType,
    ViewingState,
    DrawingState,
    ErasingState,
    SolvingState,
    SolvedState,
)
from .thread import SolverThread


class SolverGridWidget(GridWidget):
    """
    Widget that displays a grid of walls and visualizes pathfinding algorithms.
    """

    _used_brush = QtGui.QBrush(QtGui.QColor(128, 128, 128))
    _source_brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
    _target_brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
    _selected_brush = QtGui.QBrush(QtGui.QColor(163, 190, 140))

    def __init__(self, rows: int, columns: int, *args: t.Any, **kwargs: t.Any):
        """."""
        super().__init__(rows, columns, *args, **kwargs)
        self.model: SolverModel = SolverModel(
            grid=self.grid,
            source=(rows - 1, columns - 1),
            target=(0, 0),
        )
        self.model.add_observer(self.update)

        self.algorithm: PathFindingAlgorithm = AStarAlgorithm()

        self.draw_mode: DrawMode = DrawMode.walls
        self.installEventFilter(self)

        self._interval: int = 100
        self._state: SolverStateType = SolverStateType.viewing
        self._state_obj: t.Any = ViewingState()
        self._state_changed: t.List[t.Callable[[], None]] = []

        self.thread: t.Optional[SolverThread] = None

        self._settings = QtCore.QSettings('Labyrinth', 'SolverGridWidget')
        self._load_settings()

        self._used_path = QtGui.QPainterPath()
        self.set_state(self._state)

    def set_state(self, new_state: SolverStateType):
        """Change the current state of the widget and notify observers."""
        old_state = self._state
        if old_state != new_state:
            self._state_obj.on_exit(self)
            self._state = new_state
            self._state_obj = {
                SolverStateType.viewing: ViewingState(),
                SolverStateType.drawing: DrawingState(),
                SolverStateType.erasing: ErasingState(),
                SolverStateType.solving: SolvingState(),
                SolverStateType.solved: SolvedState(),
            }[new_state]
            self._state_obj.on_enter(self)

            for callback in self._state_changed:
                callback()
            self.update()

    def set_algorithm(self, algorithm: PathFindingAlgorithm):
        """Set the pathfinding algorithm to use."""
        self.algorithm = algorithm
        self.model.set_algorithm(algorithm)

    def paintEvent(self, event: QtGui.QPaintEvent):
        """Paint the grid and visualization."""
        self._render_grid_pixmap()
        painter = QtGui.QPainter(self)
        painter.translate(0.5, 0.5)
        painter.setRenderHints(painter.Antialiasing)

        painter.drawPixmap(
            self._canvas_left,
            self._canvas_top,
            self._grid_pixmap,
        )

        self._draw_source_and_target(painter)

        if self._state == SolverStateType.solving:
            self._update_used_path()
            self._draw_current_solve_step(painter)
        elif self._state == SolverStateType.solved:
            self._update_used_path()
            self._draw_result(painter)

        super().paintEvent(event)
        painter.end()

    def eventFilter(
            self,
            source: QtWidgets.QWidget,
            event: QtCore.QEvent,
    ) -> bool:
        """Filter events to handle state-specific input."""
        self._state_obj.handle_input(self, event)
        return super().eventFilter(source, event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        """
        Handle mouse movement for drawing/erasing walls or setting
        source/target.
        """
        left, top = self._canvas_left, self._canvas_top
        width, height = self._canvas_width, self._canvas_height

        x = event.pos().x()
        y = event.pos().y()

        i = floor((x - left) / self._square_size)
        j = floor((y - top) / self._square_size)

        if (left <= x <= left + width) and (top <= y <= top + height):
            if self.draw_mode == DrawMode.walls:
                if self._state == SolverStateType.drawing:
                    self.grid.try_set_cell((j, i))
                    self.invalidate_cache()
                elif self._state == SolverStateType.erasing:
                    self.grid.try_reset_cell((j, i))
                    self.invalidate_cache()

            elif self.draw_mode == DrawMode.target:
                if self._state == SolverStateType.drawing:
                    if not self.grid.get_cell((j, i)):
                        self.model.target = (j, i)

            elif self.draw_mode == DrawMode.source:
                if self._state == SolverStateType.drawing:
                    if not self.grid.get_cell((j, i)):
                        self.model.source = (j, i)

            self.update()

        super().mouseMoveEvent(event)

    def resize_grid(self, rows: int, columns: int):
        """Resize the grid and adjust source/target positions if needed."""
        self.grid.try_resize(rows, columns)

        if (
                self.model.target[0] >= self.grid.rows
                or self.model.target[1] >= self.grid.columns
        ):
            self.model.target = (0, 0)
            self.grid.try_reset_cell(self.model.target)

        if (
                self.model.source[0] >= self.grid.rows
                or self.model.source[1] >= self.grid.columns
        ):
            self.model.source = (self.grid.rows - 1, self.grid.columns - 1)
            self.grid.try_reset_cell(self.model.source)

        self._update_layout()
        self.update()

    def solve(self) -> t.List[Cell]:
        """Solve the pathfinding problem and return the path."""
        return self.algorithm.solve(
            grid=self.grid,
            source=self.model.source,
            target=self.model.target,
        )

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
        if self._state == SolverStateType.viewing:
            self._interval = new_value
            self._save_settings()

    @property
    def state(self) -> SolverStateType:
        """Get the current state."""
        return self._state

    @state.setter
    def state(self, new_state: SolverStateType):
        """Set the current state."""
        self.set_state(new_state)

    def start_solving(self):
        """Start the solving process in a separate thread."""
        self.model.reset()
        fixed_interval = int(
             self._interval * 1_000 / (self.grid.rows * self.grid.columns)
        )
        self.thread = SolverThread(
            algorithm=self.algorithm,
            grid=self.grid,
            source=self.model.source,
            target=self.model.target,
            interval_ms=fixed_interval,
        )
        self.thread.step_signal.connect(self._on_step_received)
        self.thread.finished_signal.connect(self._on_solving_finished)
        self.thread.start()
        self.set_state(SolverStateType.solving)

    def _load_settings(self):
        """Load settings from QSettings."""
        self._interval = self._settings.value("interval", 100, type=int)

    def _save_settings(self):
        """Save settings to QSettings."""
        self._settings.setValue("interval", self._interval)

    def _on_step_received(self, step: SolveStep):
        """Handle a step received from the solver thread."""
        self.model.apply_step(step)

    def _on_solving_finished(self):
        """Handle the end of the solving process."""
        self.set_state(SolverStateType.solved)

    def _draw_source_and_target(self, painter: QtGui.QPainter):
        """Draw the source and target cells on the painter."""
        left, top = self._canvas_left, self._canvas_top
        rectangle = QtCore.QRectF(0, 0, self._square_size, self._square_size)

        painter.setOpacity(1)
        painter.setBrush(SolverGridWidget._target_brush)
        painter.drawRect(rectangle.translated(
            left + self.model.target[1] * self._square_size,
            top + self.model.target[0] * self._square_size,
        ))

        painter.setBrush(SolverGridWidget._source_brush)
        painter.drawRect(rectangle.translated(
            left + self.model.source[1] * self._square_size,
            top + self.model.source[0] * self._square_size,
        ))

    def _draw_current_solve_step(self, painter: QtGui.QPainter):
        """Draw the current step of the solving process."""

        painter.setOpacity(0.5)
        painter.setBrush(SolverGridWidget._used_brush)
        painter.drawPath(self._used_path)

        current_path = self.model.get_current_path_cache()
        if current_path:
            painter.setOpacity(1)
            for node_idx, node in enumerate(current_path):
                if len(current_path) > 1:
                    hue = 2 / 3 * node_idx / (len(current_path) - 1)
                    rgb_color = colorsys.hls_to_rgb(hue, 0.5, 1)
                    r, g, b = (floor(255 * c) for c in rgb_color)
                    color = QtGui.QColor(r, g, b)
                else:
                    color = SolverGridWidget._selected_brush.color()

                painter.setBrush(color)
                x = self._canvas_left + node[1] * self._square_size
                y = self._canvas_top + node[0] * self._square_size
                painter.drawRect(
                    QtCore.QRectF(
                        x, y, self._square_size, self._square_size,
                    )
                )

    def _draw_result(self, painter: QtGui.QPainter):
        """Draw the final result of the pathfinding."""
        painter.setOpacity(0.33)
        painter.setBrush(SolverGridWidget._used_brush)
        painter.drawPath(self._used_path)

        result = self.algorithm.solve(
            grid=self.grid,
            source=self.model.source,
            target=self.model.target,
        )
        if result:
            painter.setOpacity(1)
            for node_idx, node in enumerate(result):
                if len(result) > 1:
                    hue = 2 / 3 * node_idx / (len(result) - 1)
                    rgb_color = colorsys.hls_to_rgb(hue, 0.5, 1)
                    r, g, b = (floor(255 * c) for c in rgb_color)
                    color = QtGui.QColor(r, g, b)
                else:
                    color = SolverGridWidget._selected_brush.color()

                painter.setBrush(color)
                x = self._canvas_left + node[1] * self._square_size
                y = self._canvas_top + node[0] * self._square_size
                painter.drawRect(
                    QtCore.QRectF(
                        x, y, self._square_size, self._square_size,
                    )
                )
        else:
            self.set_state(SolverStateType.viewing)
            QtCore.QTimer.singleShot(0, self._show_no_path_error)

    def _show_no_path_error(self):
        """Show an error message if no path exists."""
        message_box = QtWidgets.QMessageBox()
        message_box.setIcon(QtWidgets.QMessageBox.Warning)
        message_box.setText('Cannot exit the maze')
        message_box.setInformativeText(
            f'No path exists from point {self.model.source} '
            f'to {self.model.target}'
        )
        message_box.setWindowTitle('Error')
        message_box.exec()

    def _update_used_path(self):
        """Update the QPainterPath for used cells to optimize drawing."""
        path = QtGui.QPainterPath()
        rect = QtCore.QRectF(0, 0, self._square_size, self._square_size)

        for row, col in self.model.get_used_cells():
            x = self._canvas_left + col * self._square_size
            y = self._canvas_top + row * self._square_size
            path.addRect(rect.translated(x, y))

        self._used_path = path
