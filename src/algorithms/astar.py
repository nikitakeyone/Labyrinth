from queue import PriorityQueue
import typing as t

from grid import GridMatrix, Cell
from .base import SolveStep, SolveQueue, PathFindingAlgorithm


class AStarAlgorithm(PathFindingAlgorithm):
    """A* pathfinding algorithm."""

    @classmethod
    def solve(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> t.List[Cell]:
        """Solve using A* algorithm."""
        frontier = PriorityQueue()
        frontier.put((0, source))

        came_from: t.Dict[Cell, t.Optional[Cell]] = dict()
        cost_so_far: t.Dict[Cell, float] = dict()
        came_from[source] = None
        cost_so_far[source] = 0

        while not frontier.empty():
            _, current = frontier.get()

            if current == target:
                break

            for next_node in grid.neighbors(current):
                next_cost = cls._get_cost(current, next_node)
                new_cost = cost_so_far[current] + next_cost

                if (
                        next_node not in cost_so_far or
                        new_cost < cost_so_far[next_node]
                ):
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + cls._heuristic(next_node, target)
                    frontier.put((priority, next_node))
                    came_from[next_node] = current

        return cls.reconstruct_path(came_from, source, target)

    @classmethod
    def get_solve_queue(
            cls,
            grid: GridMatrix,
            source: Cell,
            target: Cell,
    ) -> SolveQueue:
        """Return a queue of steps for A* visualization."""
        frontier = PriorityQueue()
        frontier.put((0, source))

        came_from: t.Dict[Cell, t.Optional[Cell]] = dict()
        cost_so_far: t.Dict[Cell, float] = dict()

        came_from[source] = None
        cost_so_far[source] = 0

        queue = SolveQueue()

        while not frontier.empty():
            _, current = frontier.get()
            if current == target:
                break

            selected = set()

            for next_node in grid.neighbors(current):
                next_cost = cls._get_cost(current, next_node)
                new_cost = cost_so_far[current] + next_cost

                step = SolveStep(
                    used=list(selected),
                    path=came_from.copy(),
                    selected=next_node,
                )
                queue.enqueue(step)

                if (
                        next_node not in cost_so_far or
                        new_cost < cost_so_far[next_node]
                ):
                    selected.add(next_node)
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + cls._heuristic(next_node, target)
                    frontier.put((priority, next_node))
                    came_from[next_node] = current

        return queue

    @staticmethod
    def _heuristic(a: Cell, b: Cell) -> float:
        """Calculate the heuristic (Manhattan distance) between two points."""
        x1, y1 = a
        x2, y2 = b
        return abs(x1 - x2) + abs(y1 - y2)
