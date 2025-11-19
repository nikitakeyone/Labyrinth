import enum
import typing as t
from abc import ABC, abstractmethod

import PyQt5.QtCore as QtCore

if t.TYPE_CHECKING:
    from .solver import SolverGridWidget


class SolverStateType(enum.Enum):
    """Enum representing the different states of the solver widget."""
    viewing = 1
    drawing = 2
    erasing = 3
    solving = 4
    solved = 5


class SolverState(ABC):
    """
    Abstract base class for solver states.
    Defines the interface for state behavior.
    """

    @abstractmethod
    def on_enter(self, widget: "SolverGridWidget"):
        """Called when the state is entered."""
        pass

    @abstractmethod
    def on_exit(self, widget: "SolverGridWidget"):
        """Called when the state is exited."""
        pass

    @abstractmethod
    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """Handle input events for this state."""
        pass


class ViewingState(SolverState):
    """
    State for viewing the grid without interaction.
    """

    def on_enter(self, widget: "SolverGridWidget"):
        """Called when entering the viewing state."""
        pass

    def on_exit(self, widget: "SolverGridWidget"):
        """Called when exiting the viewing state."""
        pass

    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """Handle mouse press events to switch to drawing/erasing."""
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                widget.set_state(SolverStateType.drawing)
            elif event.button() == QtCore.Qt.RightButton:
                widget.set_state(SolverStateType.erasing)


class DrawingState(SolverState):
    """State for drawing walls on the grid."""

    def on_enter(self, widget: "SolverGridWidget"):
        """Called when entering the drawing state."""
        pass

    def on_exit(self, widget: "SolverGridWidget"):
        """Called when exiting the drawing state."""
        pass

    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """Handle mouse release to return to viewing."""
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            widget.set_state(SolverStateType.viewing)


class ErasingState(SolverState):
    """State for erasing walls from the grid."""

    def on_enter(self, widget: "SolverGridWidget"):
        """Called when entering the erasing state."""
        pass

    def on_exit(self, widget: "SolverGridWidget"):
        """Called when exiting the erasing state."""
        pass

    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """Handle mouse release to return to viewing."""
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            widget.set_state(SolverStateType.viewing)


class SolvingState(SolverState):
    """State for running the pathfinding algorithm."""

    def on_enter(self, widget: "SolverGridWidget"):
        """Start the timer when entering the solving state."""
        pass

    def on_exit(self, widget: "SolverGridWidget"):
        """Stop the timer when exiting the solving state."""
        if widget.thread:
            widget.thread.skip()

    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """No input handling in solving state."""
        pass


class SolvedState(SolverState):
    """State for displaying the solved path."""

    def on_enter(self, widget: "SolverGridWidget"):
        """Called when entering the solved state."""
        pass

    def on_exit(self, widget: "SolverGridWidget"):
        """Called when exiting the solved state."""
        pass

    def handle_input(self, widget: "SolverGridWidget", event: QtCore.QEvent):
        """No input handling in solved state."""
        pass
