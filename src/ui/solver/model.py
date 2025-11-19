import enum
import typing as t
from dataclasses import dataclass, field

from algorithms import PathFindingAlgorithm, AStarAlgorithm, SolveStep
from grid import GridMatrix, Cell


@dataclass
class SolverModel:
    """
    Model for managing the state of the pathfinding solver.

    Stores the grid, source/target positions, algorithm, and current solving
    state.
    Provides methods to update state from algorithm steps and notify observers.
    """
    grid: GridMatrix
    source: Cell
    target: Cell
    algorithm: PathFindingAlgorithm = AStarAlgorithm()

    _used: t.Set[Cell] = field(default_factory=set)
    _full_path: t.Dict[Cell, t.Optional[Cell]] = field(default_factory=dict)
    _current_cell: t.Optional[Cell] = None
    _current_path_cache: t.List[Cell] = field(default_factory=list)
    _observers: t.List[t.Callable] = field(default_factory=list)

    def add_observer(self, callback: t.Callable):
        """Add a callback to be called when the model state changes."""
        self._observers.append(callback)

    def notify_observers(self):
        """Notify all registered observers that the model state has changed."""
        for cb in self._observers:
            cb()

    def set_algorithm(self, algorithm: PathFindingAlgorithm):
        """Set the pathfinding algorithm to use."""
        self.algorithm = algorithm

    def reset(self):
        """Reset the solving state (used cells, path, current cell, etc.)."""
        self._used.clear()
        self._full_path.clear()
        self._current_cell = None
        self._current_path_cache.clear()
        self.notify_observers()

    def apply_step(self, step: SolveStep):
        """
        Apply a single step from the algorithm trace to update the model state.
        """
        if step.selected_node not in self._full_path:
            self._full_path[step.selected_node] = step.from_node
            self._used.add(step.selected_node)
        self._current_cell = step.selected_node
        self._current_path_cache.clear()
        self.notify_observers()

    def get_used_cells(self) -> t.Set[Cell]:
        """
        Get the set of cells that have been visited during the solving process.
        """
        return self._used

    def get_full_path(self) -> t.Dict[Cell, t.Optional[Cell]]:
        """Get the full path map (came_from dictionary) built so far."""
        return self._full_path

    def get_current_cell(self) -> t.Optional[Cell]:
        """Get the currently processed cell in the solving trace."""
        return self._current_cell

    def get_current_path_cache(self) -> t.List[Cell]:
        """
        Get the reconstructed path from source to the current cell.
        The path is cached to avoid repeated reconstruction.
        """
        if not self._current_path_cache and self._current_cell:
            self._current_path_cache = self.algorithm.reconstruct_path(
                came_from=self._full_path,
                source=self.source,
                target=self._current_cell,
            )
        return self._current_path_cache


class DrawMode(enum.Enum):
    """
    Enum representing the different modes for interacting with the grid.

    - walls: Draw or erase walls on the grid.
    - source: Set the starting point for pathfinding.
    - target: Set the destination point for pathfinding.
    """
    walls = 1
    source = 2
    target = 3
