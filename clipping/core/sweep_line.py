from functools import partial
from typing import (Callable,
                    Generic,
                    Optional,
                    cast)

from dendroid import red_black
from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)

from clipping.hints import Coordinate
from .event import Event


class SweepLine(Generic[Event]):
    __slots__ = 'current_x', '_tree'

    def __init__(self, current_x: Optional[Coordinate] = None) -> None:
        self.current_x = current_x
        self._tree = red_black.tree(key=cast(Callable[[Event],
                                                      SweepLineKey],
                                             partial(SweepLineKey, self)))

    __repr__ = generate_repr(__init__)

    def __contains__(self, event: Event) -> bool:
        return event in self._tree

    def move_to(self, x: Coordinate) -> None:
        self.current_x = x

    def add(self, event: Event) -> None:
        self._tree.add(event)

    def remove(self, event: Event) -> None:
        self._tree.remove(event)

    def above(self, event: Event) -> Optional[Event]:
        try:
            return self._tree.next(event)
        except ValueError:
            return None

    def below(self, event: Event) -> Optional[Event]:
        try:
            return self._tree.prev(event)
        except ValueError:
            return None


class SweepLineKey:
    __slots__ = 'sweep_line', 'event'

    def __init__(self, sweep_line: SweepLine, event: Event) -> None:
        self.sweep_line = sweep_line
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start_x, start_y = start = event.start
        other_start_x, other_start_y = other_start = other_event.start
        end_x, end_y = end = event.end
        other_end_x, other_end_y = other_end = other_event.end
        other_start_orientation = orientation(end, start, other_start)
        other_end_orientation = orientation(end, start, other_end)
        if other_start_orientation is other_end_orientation:
            if other_start_orientation is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return other_start_orientation is Orientation.COUNTERCLOCKWISE
            # segments are collinear
            elif event.from_left is not other_event.from_left:
                return event.from_left
            elif start_x == other_start_x:
                if start_y != other_start_y:
                    # segments are vertical
                    return start_y < other_start_y
                else:
                    # segments have same start
                    return end_y < other_end_y
            elif start_y != other_start_y:
                return start_y < other_start_y
            else:
                # segments are horizontal
                return start_x < other_start_x
        start_orientation = orientation(other_end, other_start, start)
        end_orientation = orientation(other_end, other_start, end)
        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif event.is_vertical:
            return start_orientation is Orientation.CLOCKWISE
        elif other_event.is_vertical:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
        elif other_end_orientation is Orientation.COLLINEAR:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            current_x = self.sweep_line.current_x
            return event.y_at(current_x) < other_event.y_at(current_x)
