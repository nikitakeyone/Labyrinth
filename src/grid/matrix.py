import typing as t

from .base import Cell


class GridMatrix:
    """Represents a grid matrix for pathfinding algorithms."""

    MIN_ROWS: t.ClassVar[int] = 10
    MIN_COLUMNS: t.ClassVar[int] = 10

    def __init__(self, rows: int, columns: int, preset: bool = False):
        """."""
        self._rows = rows
        self._columns = columns
        self._cells: t.List[t.List[bool]] = [
            [preset for _ in range(columns)] for _ in range(rows)
        ]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns

    def is_on_grid(self, node: Cell) -> bool:
        """Check if a node is within the grid boundaries."""
        x, y = node
        return 0 <= x < self._rows and 0 <= y < self._columns

    def in_bounds(self, cell: Cell) -> bool:
        """Check if a cell is within grid bounds."""
        x, y = cell
        return 0 <= x < self._rows and 0 <= y < self._columns

    def neighbors(self, cell: Cell) -> t.Iterator[Cell]:
        """Return an iterator over walkable neighbors of a given cell."""
        x, y = cell
        neighbors = [(x + 1, y), (x - 1, y), (x, y - 1), (x, y + 1)]
        if (x + y) % 2 == 0:
            neighbors.reverse()
        results = filter(self.in_bounds, neighbors)
        results = filter(lambda c: not self.get_cell(c), results)
        return results

    def try_resize(self, rows: int, columns: int) -> bool:
        """Resize the grid if new dimensions are at least 10x10."""
        if rows >= self.MIN_ROWS and columns >= self.MIN_COLUMNS:
            old_cells = self._cells
            self._cells = [
                [
                    old_cells[j][i]
                    if (j < self._rows and i < self._columns)
                    else False
                    for i in range(columns)
                ]
                for j in range(rows)
            ]
            self._rows = rows
            self._columns = columns
            return True
        return False

    def try_set_cell(self, cell: Cell) -> bool:
        """Set a cell as occupied if it's within bounds."""
        if self.in_bounds(cell):
            self._cells[cell[0]][cell[1]] = True
            return True
        return False

    def try_reset_cell(self, cell: Cell) -> bool:
        """Reset a cell to free if it's within bounds."""
        if self.in_bounds(cell):
            self._cells[cell[0]][cell[1]] = False
            return True
        return False

    def get_cell(self, cell: Cell) -> bool:
        """Get the state of a cell (True if occupied)."""
        if self.in_bounds(cell):
            return self._cells[cell[0]][cell[1]]
        return False
