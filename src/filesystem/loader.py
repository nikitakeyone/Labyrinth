from grid.matrix import GridMatrix


class Loader:
    """Loads a grid matrix from a file."""

    def __init__(self, file_path: str):
        self._file_path = file_path

    def load(self) -> GridMatrix:
        """Load the grid from the specified file."""
        try:
            with open(self._file_path, 'r') as file:
                lines = file.readlines()
        except OSError as e:
            raise GridLoadException(self._file_path) from e

        if len(lines) < 2:
            raise FileFormatException(self._file_path)

        try:
            result = GridMatrix(1, 1)

            for i, line in enumerate(lines):
                values = line.split(',')

                if i == 0:
                    if not result.try_resize(len(lines), len(values)):
                        raise FileFormatException(self._file_path)

                for j, cell in enumerate(values):
                    if cell == '1':
                        result.try_set_cell((i, j))

            return result

        except (ValueError, IndexError):
            raise FileFormatException(self._file_path)
