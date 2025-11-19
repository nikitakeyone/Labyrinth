from grid.matrix import GridMatrix

from .exceptions import GridDumpException


class Dumper:
    """Dumps a grid matrix to a file."""

    def __init__(self, grid: GridMatrix, file_path: str):
        self._file_path = file_path
        self._grid = grid

    def save(self):
        """Save the grid to the specified file."""
        try:
            with open(self._file_path, 'w') as file:
                for i in range(self._grid.rows):
                    if i != 0:
                        file.write('\n')

                    for j in range(self._grid.columns):
                        if j != 0:
                            file.write(',')
                        file.write('1' if self._grid.get_cell((i, j)) else '0')
        except OSError as e:
            raise GridDumpException from e