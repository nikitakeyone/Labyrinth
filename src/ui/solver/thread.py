import time

import PyQt5.QtCore as QtCore

from algorithms import PathFindingAlgorithm, SolveStep
from grid import GridMatrix, Cell


class SolverThread(QtCore.QThread):
    """
    A thread for running the pathfinding algorithm and emitting steps
    for visualization.
    """
    step_signal = QtCore.pyqtSignal(SolveStep)
    finished_signal = QtCore.pyqtSignal()

    def __init__(
            self,
            algorithm: PathFindingAlgorithm,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
            interval_ms: int = 100,
    ):
        super().__init__()
        self.algorithm = algorithm
        self.grid = grid
        self.source = source
        self.target = target
        self.interval_ms = interval_ms
        self.skip_flag = False

    def skip(self):
        """Set the stop flag to request the thread to stop."""
        self.skip_flag = True

    def run(self):
        """
        Execute the algorithm's solve_trace and emit steps via signals.
        Emit finished_signal when done or on error.
        """
        try:
            for step in self.algorithm.solve_trace(
                    grid=self.grid,
                    source=self.source,
                    target=self.target,
            ):
                if not self.skip_flag:
                    time.sleep(self.interval_ms / 1000.0)

                self.step_signal.emit(step)

            self.finished_signal.emit()
        except Exception as e:
            print(f"Solver thread error: {e}")
            self.finished_signal.emit()
