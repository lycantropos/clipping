from abc import (ABC,
                 abstractmethod)
from functools import partial
from typing import (Generic,
                    Optional,
                    TypeVar)

from dendroid import red_black
from ground.base import (Context,
                         Orientation)
from reprit.base import generate_repr

from .event import LeftEvent
from .hints import Orienteer

Event = TypeVar('Event',
                bound=LeftEvent)


class SweepLine(ABC, Generic[Event]):
    __slots__ = ()

    @abstractmethod
    def __contains__(self, event: Event) -> bool:
        """Checks if given event is in the sweep line."""

    @abstractmethod
    def above(self, event: Event) -> Optional[Event]:
        """Returns event which is above the given one."""

    @abstractmethod
    def add(self, event: Event) -> None:
        """Adds given event to the sweep line."""

    @abstractmethod
    def below(self, event: Event) -> Optional[Event]:
        """Returns event which is below the given one."""

    @abstractmethod
    def remove(self, event: Event) -> None:
        """Removes given event from the sweep line."""


class BinarySweepLine(SweepLine):
    __slots__ = 'context', '_set'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._set = red_black.set_(key=partial(BinarySweepLineKey,
                                               context.angle_orientation))

    def __contains__(self, event: Event) -> bool:
        return event in self._set

    def add(self, event: Event) -> None:
        self._set.add(event)

    def remove(self, event: Event) -> None:
        self._set.remove(event)

    def above(self, event: Event) -> Optional[Event]:
        try:
            return self._set.next(event)
        except ValueError:
            return None

    def below(self, event: Event) -> Optional[Event]:
        try:
            return self._set.prev(event)
        except ValueError:
            return None


class NarySweepLine(SweepLine):
    __slots__ = 'context', '_set'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._set = red_black.set_(key=partial(NarySweepLineKey,
                                               context.angle_orientation))

    def __contains__(self, event: Event) -> bool:
        return event in self._set

    def add(self, event: Event) -> None:
        self._set.add(event)

    def remove(self, event: Event) -> None:
        self._set.remove(event)

    def above(self, event: Event) -> Optional[Event]:
        try:
            return self._set.next(event)
        except ValueError:
            return None

    def below(self, event: Event) -> Optional[Event]:
        try:
            return self._set.prev(event)
        except ValueError:
            return None


class BinarySweepLineKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self, orienteer: Orienteer, event: Event) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'BinarySweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end
        other_start_orientation = self.orienteer(start, end, other_start)
        other_end_orientation = self.orienteer(start, end, other_end)
        if other_start_orientation is other_end_orientation:
            if other_start_orientation is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return other_start_orientation is Orientation.COUNTERCLOCKWISE
            # segments are collinear
            elif event.from_first is not other_event.from_first:
                return event.from_first
            elif start.x == other_start.x:
                if start.y != other_start.y:
                    # segments are vertical
                    return start.y < other_start.y
                # segments have same start
                elif end.y != other_end.y:
                    return end.y < other_end.y
                else:
                    # segments are horizontal
                    return end.x < other_end.x
            elif start.y != other_start.y:
                return start.y < other_start.y
            else:
                # segments are horizontal
                return start.x < other_start.x
        start_orientation = self.orienteer(other_start, other_end, start)
        end_orientation = self.orienteer(other_start, other_end, end)
        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE


class NarySweepLineKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self, orienteer: Orienteer, event: Event) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'NarySweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end
        other_start_orientation = self.orienteer(start, end, other_start)
        other_end_orientation = self.orienteer(start, end, other_end)
        if other_start_orientation is other_end_orientation:
            if other_start_orientation is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return other_start_orientation is Orientation.COUNTERCLOCKWISE
            # segments are collinear
            elif start.x == other_start.x:
                if start.y != other_start.y:
                    # segments are vertical
                    return start.y < other_start.y
                # segments have same start
                elif end.y != other_end.y:
                    return end.y < other_end.y
                else:
                    # segments are horizontal
                    return end.x < other_end.x
            elif start.y != other_start.y:
                return start.y < other_start.y
            else:
                # segments are horizontal
                return start.x < other_start.x
        start_orientation = self.orienteer(other_start, other_end, start)
        end_orientation = self.orienteer(other_start, other_end, end)
        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
