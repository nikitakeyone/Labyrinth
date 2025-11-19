import dataclasses as dc
import typing as t
from abc import ABC, abstractmethod

from grid import GridMatrix, Cell


@dc.dataclass
class SolveStep:
    """Represents a single step in the solving process."""

    selected_node: Cell
    from_node: Cell


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
    def solve_trace(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> t.Iterator[SolveStep]:
        """Yield steps for visualization of the pathfinding process."""
        pass

    @staticmethod
    def reconstruct_path(
            came_from: t.Dict[Cell, Cell],
            source: Cell,
            target: Cell,
    ) -> t.List[Cell]:
        """
        Reconstruct the path from source to target using the came_from map.
        """
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
    def _get_cost(from_node: Cell, to_node: Cell) -> float:
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
