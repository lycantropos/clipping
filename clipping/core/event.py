from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (Optional,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.hints import Point
from reprit.base import generate_repr

from .enums import OverlapKind
from .hints import SegmentEndpoints


class Event(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def end(self) -> Point:
        """Returns end of the event."""

    @property
    @abstractmethod
    def start(self) -> Point:
        """Returns start of the event."""

    @property
    @abstractmethod
    def is_left(self) -> bool:
        """Checks if the event's start corresponds to the leftmost endpoint."""


class LeftEvent(Event):
    is_left = True
    opposite = None  # type: Optional[RightEvent]

    __slots__ = ()

    @property
    def end(self) -> Point:
        return self.opposite.start

    @abstractmethod
    def divide(self, point: Point) -> 'Event':
        """Divides the event at given break point and returns tail."""


class RightEvent(Event):
    is_left = False
    opposite = None  # type: Optional[LeftEvent]

    __slots__ = ()

    @property
    def end(self) -> Point:
        return self.opposite.start


class LeftNaryEvent(LeftEvent):
    @classmethod
    def from_segment_endpoints(cls, segment_endpoints: SegmentEndpoints
                               ) -> 'LeftNaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        result = cls(start, None)
        result.opposite = RightNaryEvent(end, result)
        return result

    __slots__ = 'opposite', '_start'

    def __init__(self,
                 start: Point,
                 opposite: Optional['Event']) -> None:
        self.opposite, self._start = opposite, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, break_point: Point) -> 'LeftNaryEvent':
        tail = self.opposite.opposite = LeftNaryEvent(break_point,
                                                      self.opposite)
        self.opposite = RightNaryEvent(break_point, self)
        return tail


class RightNaryEvent(RightEvent):
    __slots__ = '_start',

    def __init__(self, start: Point, opposite: LeftNaryEvent) -> None:
        self.opposite, self._start = opposite, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def start(self) -> Point:
        return self._start


class LeftBinaryEvent(LeftEvent):
    @classmethod
    def from_segment_endpoints(cls,
                               segment_endpoints: SegmentEndpoints,
                               from_first: bool) -> 'LeftBinaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        event = cls(start, None, from_first)
        event.opposite = RightBinaryEvent(end, event)
        return event

    __slots__ = 'from_first', '_start'

    def __init__(self,
                 start: Point,
                 opposite: Optional['RightBinaryEvent'],
                 from_first: bool) -> None:
        self.from_first, self.opposite, self._start = (from_first, opposite,
                                                       start)

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'LeftBinaryEvent':
        tail = self.opposite.opposite = LeftBinaryEvent(point, self.opposite,
                                                        self.from_first)
        self.opposite = RightBinaryEvent(point, self)
        return tail


class RightBinaryEvent(RightEvent):
    __slots__ = '_start',

    def __init__(self,
                 start: Point,
                 opposite: LeftBinaryEvent) -> None:
        self.opposite, self._start = opposite, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first(self) -> bool:
        return self.opposite.from_first

    @property
    def start(self) -> Point:
        return self._start


class LeftMixedEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first: bool) -> 'LeftMixedEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        event = cls(start, None, from_first, inside_on_left)
        event.opposite = RightMixedEvent(end, event)
        return event

    __slots__ = ('from_first', 'in_result', 'interior_to_left', 'is_overlap',
                 'other_interior_to_left', '_start')

    def __init__(self,
                 start: Point,
                 opposite: Optional['RightMixedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 is_overlap: bool = False,
                 in_result: bool = False) -> None:
        self.opposite, self._start = opposite, start
        self.from_first = from_first
        self.interior_to_left, self.other_interior_to_left = (
            interior_to_left, other_interior_to_left)
        self.is_overlap = is_overlap
        self.in_result = in_result

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def left(self) -> 'LeftMixedEvent':
        return self

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return not self.other_interior_to_left and not self.is_overlap

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'LeftMixedEvent':
        tail = self.opposite.opposite = LeftMixedEvent(
                point, self.opposite, self.from_first, self.interior_to_left)
        self.opposite = RightMixedEvent(point, self)
        return tail


class RightMixedEvent(RightEvent):
    __slots__ = '_start',

    def __init__(self, start: Point, opposite: LeftMixedEvent) -> None:
        self.opposite, self._start = opposite, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first(self) -> bool:
        return self.opposite.from_first

    @property
    def left(self) -> LeftMixedEvent:
        return self.opposite

    @property
    def start(self) -> Point:
        return self._start


class LeftHolelessEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first: bool) -> 'LeftHolelessEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        event = cls(start, None, from_first, inside_on_left)
        event.opposite = RightShapedEvent(end, event)
        return event

    __slots__ = ('from_first', 'in_result', 'interior_to_left',
                 'other_interior_to_left', 'overlap_kind', 'position',
                 '_start')

    def __init__(self,
                 start: Point,
                 opposite: Optional['RightShapedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 position: int = 0) -> None:
        self.opposite, self._start = opposite, start
        self.from_first = from_first
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = other_interior_to_left
        self.overlap_kind = overlap_kind
        self.in_result = in_result
        self.position = position

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def is_common_polyline_component(self) -> bool:
        """
        Checks if the segment is a component of intersection's polyline.
        """
        return self.overlap_kind is OverlapKind.DIFFERENT_ORIENTATION

    @property
    def is_common_region_boundary(self) -> bool:
        """
        Checks if the segment is a boundary of intersection's region.
        """
        return self.overlap_kind is OverlapKind.SAME_ORIENTATION

    @property
    def is_overlap(self) -> bool:
        """
        Checks if the segment lies on the boundary of both operands.
        """
        return self.overlap_kind is not OverlapKind.NONE

    @property
    def left(self) -> 'LeftHolelessEvent':
        return self

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'LeftHolelessEvent':
        tail = self.opposite.opposite = LeftHolelessEvent(
                point, self.opposite, self.from_first, self.interior_to_left)
        self.opposite = RightShapedEvent(point, self)
        return tail


class LeftHoleyEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first: bool) -> 'LeftHoleyEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        event = cls(start, None, from_first, inside_on_left)
        event.opposite = RightShapedEvent(end, event)
        return event

    __slots__ = ('below_in_result_event', 'contour_id', 'from_first',
                 'in_result', 'interior_to_left', 'other_interior_to_left',
                 'overlap_kind', 'position', 'result_in_out', '_start')

    def __init__(self,
                 start: Point,
                 opposite: Optional['RightShapedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: Optional[int] = None,
                 below_in_result_event: Optional['LeftHoleyEvent'] = None
                 ) -> None:
        self.opposite, self._start = opposite, start
        self.from_first = from_first
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = other_interior_to_left
        self.overlap_kind = overlap_kind
        self.in_result = in_result
        self.position = position
        self.result_in_out = result_in_out
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def inside(self) -> bool:
        """
        Checks if the segment enclosed by
        or lies within the region of the intersection.
        """
        return (self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def is_common_polyline_component(self) -> bool:
        """
        Checks if the segment is a component of intersection's polyline.
        """
        return self.overlap_kind is OverlapKind.DIFFERENT_ORIENTATION

    @property
    def is_common_region_boundary(self) -> bool:
        """
        Checks if the segment is a boundary of intersection's region.
        """
        return self.overlap_kind is OverlapKind.SAME_ORIENTATION

    @property
    def is_overlap(self) -> bool:
        """
        Checks if the segment lies on the boundary of both operands.
        """
        return self.overlap_kind is not OverlapKind.NONE

    @property
    def is_vertical(self) -> bool:
        return self.start.x == self.end.x

    @property
    def left(self) -> 'LeftHoleyEvent':
        return self

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'LeftHoleyEvent':
        tail = self.opposite.opposite = LeftHoleyEvent(
                point, self.opposite, self.from_first, self.interior_to_left)
        self.opposite = RightShapedEvent(point, self)
        return tail


LeftShapedEvent = TypeVar('LeftShapedEvent', LeftHolelessEvent, LeftHoleyEvent)


class RightShapedEvent(RightEvent):
    __slots__ = 'position', '_start'

    def __init__(self,
                 start: Point,
                 opposite: LeftShapedEvent,
                 position: int = 0) -> None:
        self.opposite, self.position, self._start = (opposite, position,
                                                     start)

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first(self) -> bool:
        return self.opposite.from_first

    @property
    def left(self) -> LeftShapedEvent:
        return self.opposite

    @property
    def start(self) -> Point:
        return self._start


def events_to_connectivity(events: Sequence[Event]) -> Sequence[int]:
    events_count = len(events)
    result = [0] * events_count
    index = 0
    while index < events_count:
        current_start = events[index].start
        right_start_index = index
        while (index < events_count
               and events[index].start == current_start
               and not events[index].is_left):
            index += 1
        right_stop_index = index - 1
        left_start_index = index
        while index < events_count and events[index].start == current_start:
            index += 1
        left_stop_index = index - 1
        has_right_events = right_stop_index >= right_start_index
        has_left_events = left_stop_index >= left_start_index
        if has_right_events:
            result[right_start_index:right_stop_index] = range(
                    right_start_index + 1, right_stop_index + 1)
            result[right_stop_index] = (left_stop_index
                                        if has_left_events
                                        else right_start_index)
        if has_left_events:
            result[left_start_index] = (right_start_index
                                        if has_right_events
                                        else left_stop_index)
            result[left_start_index + 1:left_stop_index + 1] = range(
                    left_start_index, left_stop_index)
    return result


def event_to_segment_endpoints(event: Event) -> Tuple[Point, Point]:
    return event.start, event.end
