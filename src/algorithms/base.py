from abc import ABC, abstractmethod
from queue import Queue
import typing as t
import dataclasses as dc

from grid import GridMatrix, Cell


@dc.dataclass
class SolveStep:
    """Represents a single step in the solving process."""

    selected: Cell
    used: t.List[Cell] = dc.field(default_factory=list)
    path: t.Dict[Cell, t.Optional[Cell]] = dc.field(default_factory=dict)


class SolveQueue:
    """A queue for storing steps during pathfinding algorithm execution."""

    def __init__(self):
        self._queue = Queue()

    def enqueue(self, step: SolveStep):
        """Add a new step to the queue."""
        self._queue.put(step)

    def dequeue(self) -> SolveStep:
        """Remove and return the next step from the queue."""
        return self._queue.get()

    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self._queue.empty()


class PathFindingAlgorithm(ABC):
    """Abstract base class for pathfinding algorithms."""

    @classmethod
    @abstractmethod
    def solve(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> t.List[Cell]:
        """Solve the pathfinding problem and return the path."""
        pass

    @classmethod
    @abstractmethod
    def get_solve_queue(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> SolveQueue:
        """Return a queue of steps for visualization."""
        pass

    @staticmethod
    def reconstruct_path(
            came_from: t.Dict[Cell, Cell],
            source: Cell,
            target: Cell,
    ) -> t.List[Cell]:
        """Reconstruct the path from source to target using the came_from map."""
        if target in came_from:
            current: Cell = target
            path: t.List[Cell] = []
            while current != source:
                path.append(current)
                current = came_from[current]
            path.append(source)
            path.reverse()
            return path
        return []

    @staticmethod
    def _get_cost(from_node:Cell, to_node: Cell) -> float:
        """Calculate the cost of moving from one node to another."""
        prev_cost = 1
        nudge = 0
        x1, y1 = from_node
        x2, y2 = to_node
        if (x1 + y1) % 2 == 0 and x2 != x1:
            nudge = 1
        if (x1 + y1) % 2 == 1 and y2 != y1:
            nudge = 1
        return prev_cost + 0.001 * nudge
