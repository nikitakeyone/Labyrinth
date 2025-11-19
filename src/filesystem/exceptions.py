class GridFileException(Exception):
    """Base exception for grid file related errors."""

    def __init__(self, filename: str):
        self._filename = filename

    @property
    def filename(self):
        return self._filename

    def __str__(self):
        return self._filename


class FileFormatException(GridFileException):
    """Raised when the file format is invalid."""

    def __str__(self):
        return f'Invalid file "{self.filename}" format!'


class FileNotFoundException(GridFileException):
    """Raised when the file is not found."""

    def __str__(self):
        return f'File "{self.filename}" not found!'


class GridDumpException(GridFileException):
    """Raised when the grid dump is failed."""

    def __str__(self):
        return f'Failed to dump grid into file "{self.filename}"!'


class GridLoadException(GridFileException):
    """Raised when the grid load is failed."""

    def __str__(self):
        return f'Failed to load grid from file "{self.filename}"!'
