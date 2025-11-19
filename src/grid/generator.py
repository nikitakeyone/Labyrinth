from abc import ABC, abstractmethod
from math import floor
from random import randint
import typing as t

from .base import Cell
from .matrix import GridMatrix


class MazeGeneratingAlgorithm(ABC):
    """Abstract base class for maze generation algorithms."""

    @classmethod
    @abstractmethod
    def generate(cls, rows: int, columns: int) -> GridMatrix:
        """Generate a maze and return the grid."""
        pass


class DfsMazeGenerator(MazeGeneratingAlgorithm):
    """Generates a maze using Depth-First Search with backtracking."""

    @staticmethod
    def is_not_corner(node: Cell, x: int, y: int) -> bool:
        """Check if a node is not on a corner relative to (x, y)."""
        return node[0] == x or node[1] == y

    @staticmethod
    def is_not_node(node: Cell, x: int, y: int) -> bool:
        """Check if a node is different from (x, y)."""
        return node[0] != x or node[1] != y

    @classmethod
    def _find_neighbors(
            cls,
            matrix: GridMatrix,
            node: Cell,
    ) -> t.List[t.Tuple[int, int]]:
        """Find valid neighbors for a given node."""
        neighbors = []
        x, y = node
        for dy in range(-2, 3, 2):
            for dx in range(-2, 3, 2):
                nx, ny = x + dx, y + dy
                if (matrix.is_on_grid((nx, ny)) and
                    cls.is_not_corner((nx, ny), x, y) and
                    cls.is_not_node((nx, ny), x, y)):
                    neighbors.append((nx, ny))
        return neighbors

    @classmethod
    def generate(cls, rows: int, columns: int) -> GridMatrix:
        """Generate a maze using DFS algorithm."""
        result = GridMatrix(rows, columns, preset=True)

        # Clear the last row if it's beyond the odd-numbered boundary
        for x in range(floor((result.rows - 1) / 2) * 2 + 1, result.rows):
            for y in range(result.columns):
                result.try_reset_cell((x, y))

        # Clear the last column if it's beyond the odd-numbered boundary
        for y in range(floor((result.columns - 1) / 2) * 2 + 1, result.columns):
            for x in range(result.rows):
                result.try_reset_cell((x, y))

        # Start at a random even coordinate
        start_x = randint(0, floor((result.rows - 1) / 2)) * 2
        start_y = randint(0, floor((result.columns - 1) / 2)) * 2

        visited: t.Set[t.Tuple[int, int]] = set()
        path_stack: t.List[t.Tuple[int, int]] = [(start_x, start_y)]
        visited.add((start_x, start_y))

        while path_stack:
            current_cell = path_stack.pop()
            neighbors = [
                n for n in cls._find_neighbors(result, current_cell)
                if n not in visited
            ]

            if neighbors:
                random_index = randint(0, len(neighbors) - 1)

                for i, neighbor in enumerate(neighbors):
                    result.try_reset_cell(neighbor)
                    visited.add(neighbor)

                    # Carve a path between current cell and neighbor
                    cx, cy = current_cell
                    nx, ny = neighbor
                    if nx == cx:
                        wall_y = (cy + ny) // 2
                        result.try_reset_cell((cx, wall_y))
                    elif ny == cy:
                        wall_x = (cx + nx) // 2
                        result.try_reset_cell((wall_x, cy))

                    if i != random_index:
                        path_stack.append(neighbor)

                path_stack.append(neighbors[random_index])

        return result
