import typing as t
from math import floor

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import Qt

from algorithms import (
    PathFindingAlgorithm,
    AStarAlgorithm,
    DijkstraAlgorithm,
    BfsAlgorithm,
)
from filesystem.dumper import Dumper
from filesystem.exceptions import GridFileException
from filesystem.loader import Loader
from grid.generator import DfsMazeGenerator
from .solver import SolverGridWidget


class MainWindow(QtWidgets.QMainWindow):
    """Main application window for the pathfinding visualizer."""

    def __init__(self):
        super().__init__()
        self.algorithms: t.Dict[str, t.Type[PathFindingAlgorithm]] = {
            "A*": AStarAlgorithm,
            "Dijkstra Search": DijkstraAlgorithm,
            "Breadth-first Search": BfsAlgorithm,
        }
        self.setup_ui()

        self.grid_widget.add_state_callback(self._on_state_changed)

    def _disable_grid_editing(self):
        """Disable UI elements related to grid editing."""
        self.row_slider.setEnabled(False)
        self.column_slider.setEnabled(False)
        self.random_walls_button.setEnabled(False)
        self.draw_mode_combo_box.setEnabled(False)
        self.algorithm_combo_box.setEnabled(False)
        self.interval_slider.setEnabled(False)
        self.filepicker_load_button.setEnabled(False)
        self.filepicker_save_button.setEnabled(False)

    def _enable_grid_editing(self):
        """Enable UI elements related to grid editing."""
        self.row_slider.setEnabled(True)
        self.column_slider.setEnabled(True)
        self.random_walls_button.setEnabled(True)
        self.draw_mode_combo_box.setEnabled(True)
        self.algorithm_combo_box.setEnabled(True)
        self.interval_slider.setEnabled(True)
        self.filepicker_load_button.setEnabled(True)
        self.filepicker_save_button.setEnabled(True)

    def _on_state_changed(self):
        """Handle changes in the solver's state."""
        if self.grid_widget.state == SolverGridWidget.State.solving:
            self.start_button.setText("Skip")
            self._disable_grid_editing()
        elif self.grid_widget.state == SolverGridWidget.State.solved:
            self.start_button.setText("Finish")
        elif self.grid_widget.state == SolverGridWidget.State.viewing:
            self.start_button.setText("Start")
            self._enable_grid_editing()

    def _process_start_button(self):
        """Handle the start button click based on current state."""
        if self.grid_widget.state == SolverGridWidget.State.solving:
            self.grid_widget.state = SolverGridWidget.State.solved
        elif self.grid_widget.state == SolverGridWidget.State.solved:
            self.grid_widget.state = SolverGridWidget.State.viewing
        elif self.grid_widget.state == SolverGridWidget.State.viewing:
            self.grid_widget.state = SolverGridWidget.State.solving

    def _resize_grid(self):
        """Resize the grid based on slider values."""
        new_rows = floor(self.row_slider.value() / 100 * 90) + 10
        new_cols = floor(self.column_slider.value() / 100 * 90) + 10
        self.grid_widget.resize_grid(new_rows, new_cols)

        self.row_label.setText(f"Number of rows: {self.grid_widget.grid.rows}")
        self.column_label.setText(
            f"Number of columns: "
            f"{self.grid_widget.grid.columns}",
        )

    def _generate_random_grid(self):
        """Generate a random maze in the grid."""
        self.grid_widget.grid = DfsMazeGenerator.generate(
            self.grid_widget.grid.rows, self.grid_widget.grid.columns
        )

        if self.grid_widget.grid.get_cell(self.grid_widget.target):
            self.grid_widget.grid.try_reset_cell(self.grid_widget.target)

        if self.grid_widget.grid.get_cell(self.grid_widget.source):
            self.grid_widget.grid.try_reset_cell(self.grid_widget.source)

        self.update()

    def _set_walls_draw_mode(self):
        """Set the draw mode to walls."""
        self.grid_widget.draw_mode = SolverGridWidget.DrawMode.walls

    def _set_target_draw_mode(self):
        """Set the draw mode to target."""
        self.grid_widget.draw_mode = SolverGridWidget.DrawMode.target

    def _set_source_draw_mode(self):
        """Set the draw mode to source."""
        self.grid_widget.draw_mode = SolverGridWidget.DrawMode.source

    def _draw_mode_change_handler(self):
        """Handle changes in the draw mode combo box."""
        commands = [
            self._set_walls_draw_mode,
            self._set_target_draw_mode,
            self._set_source_draw_mode,
        ]
        commands[self.draw_mode_combo_box.currentIndex()]()

    def _algorithm_change_handler(self):
        """Handle changes in the algorithm combo box."""
        self.grid_widget.set_algorithm(
            self.algorithms[self.algorithm_combo_box.currentText()](),
        )

    def _change_interval(self):
        """Change the animation interval based on the slider."""
        new_interval = floor(self.interval_slider.value() / 100 * 990) + 10
        self.grid_widget.interval = new_interval

    def _save_file(self):
        """Save the current grid to a file."""
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Grid", "", "CSV Files (*.csv)"
        )

        if filename:
            saver = Dumper(self.grid_widget.grid, filename)

            try:
                saver.save()
            except GridFileException as e:
                message_box = QtWidgets.QMessageBox()
                message_box.setIcon(QtWidgets.QMessageBox.Warning)
                message_box.setText("Error saving file!")
                message_box.setInformativeText(str(e))
                message_box.setWindowTitle("Error!")
                message_box.exec()

    def _load_file(self):
        """Load a grid from a file."""
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("CSV Files (*.csv)")

        if file_dialog.exec():
            filename = file_dialog.selectedFiles()[0]

            loader = Loader(filename)

            try:
                loaded_grid = loader.load()
                self.grid_widget.grid = loaded_grid
                self.grid_widget.resize_grid(
                    loaded_grid.rows,
                    loaded_grid.columns,
                )
                self.update()

                self.row_slider.setValue(
                    int(floor(10 * loaded_grid.rows - 100) / 9)),
                self.column_slider.setValue(
                    int(floor(10 * loaded_grid.columns - 100) / 9),
                )

            except GridFileException as e:
                message_box = QtWidgets.QMessageBox(file_dialog)
                message_box.setIcon(QtWidgets.QMessageBox.Warning)
                message_box.setText("Error loading file!")
                message_box.setInformativeText(str(e))
                message_box.setWindowTitle("Error!")
                message_box.exec()

    def _setup_file_group_box(self):
        """Setup the file operations group box."""
        self.filepicker_group_box = QtWidgets.QGroupBox(
            self.settings_group_box,
        )
        self.filepicker_group_box.setTitle("File System")

        self.filepicker_layout_widget = QtWidgets.QWidget(
            self.filepicker_group_box,
        )
        self.filepicker_layout_widget.setObjectName("filepickerLayoutWidget")
        self.filepicker_layout_widget.setGeometry(QtCore.QRect(8, 16, 150, 128))

        layout = QtWidgets.QVBoxLayout(self.filepicker_layout_widget)
        self.settings_layout.addWidget(self.filepicker_group_box)

        self.filepicker_load_button = QtWidgets.QPushButton()
        self.filepicker_load_button.setObjectName("filepickerLoadButton")
        self.filepicker_load_button.setText("Load")
        self.filepicker_load_button.clicked.connect(self._load_file)
        layout.addWidget(self.filepicker_load_button)

        self.filepicker_save_button = QtWidgets.QPushButton()
        self.filepicker_save_button.setObjectName("filepickerSaveButton")
        self.filepicker_save_button.setText("Save")
        self.filepicker_save_button.clicked.connect(self._save_file)
        layout.addWidget(self.filepicker_save_button)

        self.filepicker_group_box.setLayout(layout)

    def _setup_grid_size_group_box(self):
        """Setup the grid size group box."""
        self.grid_size_group_box = QtWidgets.QGroupBox(self.settings_group_box)
        self.grid_size_group_box.setObjectName("gridSizeGroupBox")
        self.grid_size_group_box.setTitle("Size")

        self.grid_size_layout_widget = QtWidgets.QWidget(
            self.grid_size_group_box,
        )
        self.grid_size_layout_widget.setObjectName("gridSizeLayoutWidget")
        self.grid_size_layout_widget.setGeometry(QtCore.QRect(8, 16, 150, 128))

        self.grid_size_layout = QtWidgets.QVBoxLayout(
            self.grid_size_layout_widget,
        )
        self.grid_size_layout.setObjectName("gridSizeLayout")
        self.grid_size_layout.setContentsMargins(8, 8, 8, 8)
        self.settings_layout.addWidget(self.grid_size_group_box)

        self.row_label = QtWidgets.QLabel(self.grid_size_layout_widget)
        self.row_label.setObjectName("rowLabel")
        self.grid_size_layout.addWidget(self.row_label)

        self.row_slider = QtWidgets.QSlider(self.grid_size_layout_widget)
        self.row_slider.setObjectName("rowSlider")
        self.row_slider.setOrientation(Qt.Horizontal)
        self.row_slider.setValue(45)
        self.grid_size_layout.addWidget(self.row_slider)

        self.column_label = QtWidgets.QLabel(self.grid_size_layout_widget)
        self.column_label.setObjectName("columnLabel")
        self.grid_size_layout.addWidget(self.column_label)

        self.column_slider = QtWidgets.QSlider(self.settings_layout_widget)
        self.column_slider.setObjectName("columnSlider")
        self.column_slider.setOrientation(Qt.Horizontal)
        self.column_slider.setValue(45)
        self.grid_size_layout.addWidget(self.column_slider)
        self.grid_size_group_box.setMinimumHeight(144)

    def _setup_maze_generation_group_box(self):
        """Setup the maze generation group box."""
        self.maze_generation_group_box = QtWidgets.QGroupBox(
            self.settings_layout_widget,
        )
        self.maze_generation_group_box.setObjectName("mazeGenerationGroupBox")
        self.maze_generation_group_box.setTitle("Maze Generation")

        self.maze_generation_layout_widget = QtWidgets.QWidget(
            self.maze_generation_group_box,
        )
        self.maze_generation_layout_widget.setObjectName(
            "mazeGenerationLayoutWidget",
        )
        self.maze_generation_layout_widget.setGeometry(
            QtCore.QRect(8, 8, 150, 64),
        )

        self.maze_generation_layout = QtWidgets.QVBoxLayout(
            self.maze_generation_layout_widget,
        )
        self.maze_generation_layout.setObjectName("mazeGenerationLayout")
        self.maze_generation_layout.setContentsMargins(8, 8, 8, 8)
        self.settings_layout.addWidget(self.maze_generation_group_box)

        self.random_walls_button = QtWidgets.QPushButton(
            self.maze_generation_group_box,
        )
        self.random_walls_button.setObjectName("randomWallsButton")
        self.random_walls_button.setText("Generate Walls")
        self.random_walls_button.clicked.connect(self._generate_random_grid)
        self.maze_generation_layout.addWidget(self.random_walls_button)

    def _setup_settings_group_box(self):
        """Setup the main settings group box."""
        self.settings_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.settings_group_box.setObjectName("settingsGroupBox")
        self.settings_group_box.setTitle("Maze Grid Editing")
        self.settings_group_box.setFixedHeight(410)

        self.settings_layout_widget = QtWidgets.QWidget(self.settings_group_box)
        self.settings_layout_widget.setObjectName("settingsLayoutWidget")
        self.settings_layout_widget.setGeometry(QtCore.QRect(8, 16, 176, 390))

        self.settings_layout = QtWidgets.QVBoxLayout(
            self.settings_layout_widget,
        )
        self.settings_layout.setObjectName("settingsLayout")
        self.settings_layout.setContentsMargins(8, 8, 8, 8)
        self.vertical_layout.addWidget(self.settings_group_box)

        self._setup_file_group_box()
        self._setup_grid_size_group_box()
        self._setup_maze_generation_group_box()
        self._setup_paint_group_box()

    def _setup_paint_group_box(self):
        """Setup the drawing mode group box."""
        self.paint_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.paint_group_box.setObjectName("paintGroupBox")
        self.paint_group_box.setTitle("Drawing")

        self.paint_layout_widget = QtWidgets.QWidget(self.paint_group_box)
        self.paint_layout_widget.setObjectName("paintLayoutWidget")
        self.paint_layout_widget.setGeometry(QtCore.QRect(8, 8, 150, 64))

        self.paint_layout = QtWidgets.QVBoxLayout(self.paint_layout_widget)
        self.paint_layout.setObjectName("paintLayout")
        self.paint_layout.setContentsMargins(8, 8, 8, 8)

        self.draw_mode_combo_box = QtWidgets.QComboBox(self.paint_layout_widget)
        self.draw_mode_combo_box.addItems(["Walls", "Target", "Source"])
        self.draw_mode_combo_box.setObjectName("drawModeComboBox")
        self.paint_layout.addWidget(self.draw_mode_combo_box)
        self.draw_mode_combo_box.currentIndexChanged.connect(
            self._draw_mode_change_handler,
        )

        self.settings_layout.addWidget(self.paint_group_box)

    def _setup_algorithm_group_box(self):
        """Setup the algorithm control group box."""
        self.algorithm_group_box = QtWidgets.QGroupBox(self.centralwidget)
        self.algorithm_group_box.setObjectName("algorithmGroupBox")
        self.algorithm_group_box.setTitle("Algorithm Control")

        self.algorithm_layout_widget = QtWidgets.QWidget(
            self.algorithm_group_box,
        )
        self.algorithm_layout_widget.setObjectName("algorithmLayoutWidget")
        self.algorithm_layout_widget.setGeometry(QtCore.QRect(8, 16, 166, 128))
        self.algorithm_layout_widget.setFixedHeight(128)

        self.algorithm_layout = QtWidgets.QVBoxLayout(
            self.algorithm_layout_widget,
        )
        self.algorithm_layout.setObjectName("algorithmLayout")
        self.algorithm_layout.setContentsMargins(8, 8, 8, 8)

        self.algorithm_label = QtWidgets.QLabel(self.algorithm_layout_widget)
        self.algorithm_label.setObjectName("algorithmLabel")
        self.algorithm_label.setText("Algorithm:")
        self.algorithm_layout.addWidget(self.algorithm_label)

        self.algorithm_combo_box = QtWidgets.QComboBox(
            self.algorithm_layout_widget,
        )

        for name in self.algorithms.keys():
            self.algorithm_combo_box.addItem(name)

        self.algorithm_combo_box.setObjectName("algorithmComboBox")
        self.algorithm_combo_box.currentIndexChanged.connect(
            self._algorithm_change_handler,
        )
        self.algorithm_layout.addWidget(self.algorithm_combo_box)

        self.interval_label = QtWidgets.QLabel(self.algorithm_layout_widget)
        self.interval_label.setObjectName("intervalLabel")
        self.interval_label.setText("Delay:")
        self.algorithm_layout.addWidget(self.interval_label)

        self.interval_slider = QtWidgets.QSlider(self.algorithm_layout_widget)
        self.interval_slider.setObjectName("intervalSlider")
        self.interval_slider.setOrientation(Qt.Horizontal)
        self.interval_slider.setValue(45)
        self.algorithm_layout.addWidget(self.interval_slider)
        self.interval_slider.valueChanged.connect(self._change_interval)

        self.start_button = QtWidgets.QPushButton(self.algorithm_layout_widget)
        self.start_button.setObjectName("startButton")
        self.start_button.setText("Start")
        self.start_button.clicked.connect(self._process_start_button)
        self.algorithm_layout.addWidget(self.start_button)

        self.vertical_layout.addWidget(self.algorithm_group_box)
        self.horizontal_layout.addWidget(self.vertical_layout_widget)

    def setup_ui(self):
        """Setup the main UI layout."""
        self.setObjectName("MainWindow")
        self.setMinimumSize(824, 624)

        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.grid_layout = QtWidgets.QGridLayout(self.centralwidget)
        self.grid_layout.setObjectName("gridLayout")

        self.horizontal_layout = QtWidgets.QHBoxLayout()
        self.horizontal_layout.setObjectName("horizontalLayout")
        self.horizontal_layout.setContentsMargins(8, 8, 8, 8)
        self.horizontal_layout.setAlignment(Qt.AlignCenter)

        self.vertical_layout_widget = QtWidgets.QWidget(self.centralwidget)
        self.vertical_layout_widget.setObjectName("verticalLayoutWidget")
        self.vertical_layout_widget.setGeometry(QtCore.QRect(0, 0, 210, 582))
        self.vertical_layout_widget.setFixedSize(210, 582)

        self.vertical_layout = QtWidgets.QVBoxLayout(
            self.vertical_layout_widget,
        )
        self.vertical_layout.setObjectName("verticalLayout")

        self._setup_settings_group_box()
        self._setup_algorithm_group_box()

        self.grid_widget = SolverGridWidget(50, 50, self.centralwidget)
        self.grid_widget.setObjectName("gridSolver")

        self.row_label.setText(f"Number of rows: {self.grid_widget.grid.rows}")
        self.column_label.setText(
            "Number of columns: "
            f"{self.grid_widget.grid.columns}",
        )

        self.row_slider.valueChanged.connect(self._resize_grid)
        self.column_slider.valueChanged.connect(self._resize_grid)

        self.horizontal_layout.addWidget(self.grid_widget)

        self.grid_layout.addLayout(self.horizontal_layout, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(self)
