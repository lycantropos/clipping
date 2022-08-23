import sys
from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (Optional,
                    Sequence,
                    TypeVar)

from ground.hints import Point
from reprit.base import generate_repr

from .enums import OverlapKind
from .hints import SegmentEndpoints

UNDEFINED_INDEX = sys.maxsize


class Event(ABC):
    start: Point

    __slots__ = ()

    @property
    def end(self) -> Point:
        return self.opposite.start

    @property
    @abstractmethod
    def is_left(self) -> bool:
        """Checks if the event's start corresponds to the leftmost endpoint."""

    @property
    @abstractmethod
    def opposite(self) -> 'Event':
        """Returns opposite of the event."""


class LeftEvent(Event):
    is_left = True

    __slots__ = 'right',

    @property
    def opposite(self) -> 'RightEvent':
        return self.right

    @abstractmethod
    def divide(self, point: Point) -> 'Event':
        """Divides the event at given break point and returns tail."""


class RightEvent(Event):
    is_left = False

    @property
    def opposite(self) -> LeftEvent:
        return self.left

    __slots__ = 'left',


class LeftNaryEvent(LeftEvent):
    @classmethod
    def from_segment_endpoints(cls, segment_endpoints: SegmentEndpoints
                               ) -> 'LeftNaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        result = cls(start, None)
        result.right = RightNaryEvent(end, result)
        return result

    __slots__ = '_start',

    def __init__(self,
                 start: Point,
                 right: Optional['RightNaryEvent']) -> None:
        self.right, self._start = right, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, break_point: Point) -> 'LeftNaryEvent':
        tail = self.right.left = LeftNaryEvent(break_point, self.right)
        self.right = RightNaryEvent(break_point, self)
        return tail


class RightNaryEvent(RightEvent):
    __slots__ = 'start',

    def __init__(self, start: Point, left: LeftNaryEvent) -> None:
        self.left, self.start = left, start

    __repr__ = recursive_repr()(generate_repr(__init__))


class LeftBinaryEvent(LeftEvent):
    @classmethod
    def from_segment_endpoints(cls,
                               segment_endpoints: SegmentEndpoints,
                               from_first: bool) -> 'LeftBinaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        event = cls(start, None, from_first)
        event.right = RightBinaryEvent(end, event)
        return event

    __slots__ = 'from_first', 'start'

    def __init__(self,
                 start: Point,
                 right: Optional['RightBinaryEvent'],
                 from_first: bool) -> None:
        self.from_first, self.right, self.start = from_first, right, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    def divide(self, point: Point) -> 'LeftBinaryEvent':
        tail = self.right.left = LeftBinaryEvent(point, self.right,
                                                 self.from_first)
        self.right = RightBinaryEvent(point, self)
        return tail


class RightBinaryEvent(RightEvent):
    __slots__ = 'start',

    def __init__(self, start: Point, left: LeftBinaryEvent) -> None:
        self.left, self.start = left, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first(self) -> bool:
        return self.left.from_first


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
        result = cls(start, None, from_first, inside_on_left)
        result.right = RightMixedEvent(end, result)
        return result

    __slots__ = ('from_first', 'from_result', 'interior_to_left', 'is_overlap',
                 'other_interior_to_left', 'start')

    def __init__(self,
                 start: Point,
                 right: Optional['RightMixedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 is_overlap: bool = False,
                 from_result: bool = False) -> None:
        self.right, self.start = right, start
        self.from_first = from_first
        self.interior_to_left, self.other_interior_to_left = (
            interior_to_left, other_interior_to_left)
        self.is_overlap = is_overlap
        self.from_result = from_result

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return not self.other_interior_to_left and not self.is_overlap

    @property
    def primary(self) -> 'LeftMixedEvent':
        return self

    def divide(self, point: Point) -> 'LeftMixedEvent':
        tail = self.right.left = LeftMixedEvent(
                point, self.right, self.from_first, self.interior_to_left)
        self.right = RightMixedEvent(point, self)
        return tail


class RightMixedEvent(RightEvent):
    __slots__ = 'start',

    def __init__(self, start: Point, left: LeftMixedEvent) -> None:
        self.left, self.start = left, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first(self) -> bool:
        return self.left.from_first

    @property
    def primary(self) -> LeftMixedEvent:
        return self.left


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
        event.right = RightShapedEvent(end, event)
        return event

    __slots__ = ('from_first', 'from_shaped_result', 'interior_to_left',
                 'other_interior_to_left', 'overlap_kind', 'position',
                 'start')

    def __init__(self,
                 start: Point,
                 right: Optional['RightShapedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 from_shaped_result: bool = False,
                 position: int = 0) -> None:
        self.right, self.start = right, start
        self.from_first = from_first
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = other_interior_to_left
        self.overlap_kind = overlap_kind
        self.from_shaped_result = from_shaped_result
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
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def primary(self) -> 'LeftHolelessEvent':
        return self

    @property
    def wholly_in_complete_intersection(self) -> bool:
        """
        Checks if the segment wholly is a part of the complete intersection.
        """
        return self.from_shaped_result or self.is_common_polyline_component

    def divide(self, point: Point) -> 'LeftHolelessEvent':
        tail = self.right.left = LeftHolelessEvent(
                point, self.right, self.from_first, self.interior_to_left
        )
        self.right = RightShapedEvent(point, self)
        return tail


class LeftHoleyEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first: bool) -> 'LeftHoleyEvent':
        start, end = segment_endpoints
        interior_to_left = True
        if start > end:
            start, end = end, start
            interior_to_left = False
        event = cls(start, None, from_first, interior_to_left)
        event.right = RightShapedEvent(end, event)
        return event

    __slots__ = ('below_event_from_shaped_result', 'contour_id', 'from_first',
                 'from_in_to_out', 'from_shaped_result', 'interior_to_left',
                 'other_interior_to_left', 'overlap_kind', 'position',
                 'start', 'start_index')

    def __init__(self,
                 start: Point,
                 right: Optional['RightShapedEvent'],
                 from_first: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 from_shaped_result: bool = False,
                 from_in_to_out: bool = False,
                 position: int = UNDEFINED_INDEX,
                 start_index: int = UNDEFINED_INDEX,
                 contour_id: Optional[int] = None,
                 below_event_from_shaped_result: Optional['LeftHoleyEvent']
                 = None) -> None:
        self.right, self.start = right, start
        self.from_first = from_first
        self.from_shaped_result = from_shaped_result
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = other_interior_to_left
        self.overlap_kind = overlap_kind
        self.position = position
        self.start_index = start_index
        self.from_in_to_out = from_in_to_out
        self.contour_id = contour_id
        self.below_event_from_shaped_result = below_event_from_shaped_result

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end_index(self) -> int:
        return self.opposite.start_index

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
    def primary(self) -> 'LeftHoleyEvent':
        return self

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)

    @property
    def wholly_in_complete_intersection(self) -> bool:
        """
        Checks if the segment wholly is a part of the complete intersection.
        """
        return self.from_shaped_result or self.is_common_polyline_component

    def divide(self, point: Point) -> 'LeftHoleyEvent':
        tail = self.right.left = LeftHoleyEvent(
                point, self.right, self.from_first, self.interior_to_left
        )
        self.right = RightShapedEvent(point, self)
        return tail


LeftShapedEvent = TypeVar('LeftShapedEvent', LeftHolelessEvent, LeftHoleyEvent)


class RightShapedEvent(RightEvent):
    __slots__ = 'position', 'start', 'start_index'

    def __init__(self,
                 start: Point,
                 left: LeftShapedEvent,
                 position: int = UNDEFINED_INDEX,
                 start_index: int = UNDEFINED_INDEX) -> None:
        self.left, self.position, self.start, self.start_index = (
            left, position, start, start_index
        )

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end_index(self) -> int:
        return self.opposite.start_index

    @property
    def from_first(self) -> bool:
        return self.left.from_first

    @property
    def primary(self) -> LeftShapedEvent:
        return self.left


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
                    right_start_index + 1, right_stop_index + 1
            )
            result[right_stop_index] = (left_stop_index
                                        if has_left_events
                                        else right_start_index)
        if has_left_events:
            result[left_start_index] = (right_start_index
                                        if has_right_events
                                        else left_stop_index)
            result[left_start_index + 1:left_stop_index + 1] = range(
                    left_start_index, left_stop_index
            )
    return result
