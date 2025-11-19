from queue import Queue
import typing as t

from grid import GridMatrix, Cell
from .base import SolveStep, SolveQueue, PathFindingAlgorithm


class BfsAlgorithm(PathFindingAlgorithm):
    """Breadth-First Search pathfinding algorithm."""

    @classmethod
    def solve(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> t.List[Cell]:
        """Solve using BFS."""
        frontier = Queue()
        frontier.put(source)

        came_from: t.Dict[Cell, t.Optional[Cell]] = dict()
        came_from[source] = None

        while not frontier.empty():
            current = frontier.get()
            if current == target:
                break

            for next_node in grid.neighbors(current):
                if next_node not in came_from:
                    frontier.put(next_node)
                    came_from[next_node] = current

        return cls.reconstruct_path(came_from, source, target)

    @classmethod
    def get_solve_queue(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> SolveQueue:
        """Return a queue of steps for BFS visualization."""
        frontier = Queue()
        frontier.put(source)

        came_from: t.Dict[Cell, t.Optional[Cell]] = dict()
        came_from[source] = None

        queue = SolveQueue()

        while not frontier.empty():
            current = frontier.get()
            if current == target:
                break

            selected = set()

            for next_node in grid.neighbors(current):
                step = SolveStep(
                    selected=next_node,
                    used=list(selected),
                    path=came_from.copy(),
                )
                queue.enqueue(step)

                if next_node not in came_from:
                    selected.add(next_node)
                    frontier.put(next_node)
                    came_from[next_node] = current

        return queue