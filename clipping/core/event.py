import sys
from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (Optional,
                    Sequence,
                    TypeVar)

from ground.hints import Point
from reprit import seekers
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
    def from_segment_endpoints(
            cls, segment_endpoints: SegmentEndpoints
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
                               from_first_operand: bool) -> 'LeftBinaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        event = cls(start, None, from_first_operand)
        event.right = RightBinaryEvent(end, event)
        return event

    __slots__ = 'from_first_operand', 'start'

    def __init__(self,
                 start: Point,
                 right: Optional['RightBinaryEvent'],
                 from_first_operand: bool) -> None:
        self.from_first_operand, self.right, self.start = (
            from_first_operand, right, start
        )

    __repr__ = recursive_repr()(generate_repr(__init__))

    def divide(self, point: Point) -> 'LeftBinaryEvent':
        tail = self.right.left = LeftBinaryEvent(point, self.right,
                                                 self.from_first_operand)
        self.right = RightBinaryEvent(point, self)
        return tail


class RightBinaryEvent(RightEvent):
    __slots__ = 'start',

    def __init__(self, start: Point, left: LeftBinaryEvent) -> None:
        self.left, self.start = left, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first_operand(self) -> bool:
        return self.left.from_first_operand


class LeftMixedEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first_operand: bool) -> 'LeftMixedEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        result = cls(start, None, from_first_operand, inside_on_left)
        result.right = RightMixedEvent(end, result)
        return result

    __slots__ = ('from_first_operand', 'from_result', 'interior_to_left',
                 'is_overlap', 'other_interior_to_left', 'start')

    def __init__(self,
                 start: Point,
                 right: Optional['RightMixedEvent'],
                 from_first_operand: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 is_overlap: bool = False,
                 from_result: bool = False) -> None:
        self.right, self.start = right, start
        self.from_first_operand = from_first_operand
        self.interior_to_left, self.other_interior_to_left = (
            interior_to_left, other_interior_to_left
        )
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
                point, self.right, self.from_first_operand,
                self.interior_to_left
        )
        self.right = RightMixedEvent(point, self)
        return tail


class RightMixedEvent(RightEvent):
    __slots__ = 'start',

    def __init__(self, start: Point, left: LeftMixedEvent) -> None:
        self.left, self.start = left, start

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def from_first_operand(self) -> bool:
        return self.left.from_first_operand

    @property
    def primary(self) -> LeftMixedEvent:
        return self.left


class LeftHolelessEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first_operand: bool) -> 'LeftHolelessEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        event = cls(start, None, from_first_operand, inside_on_left)
        event.right = RightShapedEvent(end, event)
        return event

    __slots__ = ('from_first_operand', 'from_shaped_result', 'id',
                 'interior_to_left', 'other_interior_to_left', 'overlap_kind',
                 'start')

    def __init__(self,
                 start: Point,
                 right: Optional['RightShapedEvent'],
                 from_first_operand: bool,
                 interior_to_left: bool,
                 *,
                 from_shaped_result: bool = False,
                 id_: int = 0,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE) -> None:
        (
            self.from_first_operand, self.from_shaped_result, self.id,
            self.interior_to_left, self.other_interior_to_left,
            self.overlap_kind, self.right, self.start
        ) = (
            from_first_operand, from_shaped_result, id_, interior_to_left,
            other_interior_to_left, overlap_kind, right, start
        )

    __repr__ = recursive_repr()(generate_repr(__init__,
                                              field_seeker=seekers.complex_))

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
                point, self.right, self.from_first_operand,
                self.interior_to_left
        )
        self.right = RightShapedEvent(point, self)
        return tail


class LeftHoleyEvent(LeftEvent):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_first_operand: bool) -> 'LeftHoleyEvent':
        start, end = segment_endpoints
        interior_to_left = True
        if start > end:
            start, end = end, start
            interior_to_left = False
        event = cls(start, None, from_first_operand, interior_to_left)
        event.right = RightShapedEvent(end, event)
        return event

    __slots__ = ('below_event_from_shaped_result', 'contour_id',
                 'from_first_operand', 'from_in_to_out', 'from_shaped_result',
                 'interior_to_left', 'other_interior_to_left', 'overlap_kind',
                 'id', 'start', 'start_id')

    def __init__(
            self,
            start: Point,
            right: Optional['RightShapedEvent'],
            from_first_operand: bool,
            interior_to_left: bool,
            *,
            below_event_from_shaped_result: Optional['LeftHoleyEvent'] = None,
            contour_id: Optional[int] = None,
            from_in_to_out: bool = False,
            from_shaped_result: bool = False,
            id_: int = UNDEFINED_INDEX,
            other_interior_to_left: bool = False,
            overlap_kind: OverlapKind = OverlapKind.NONE,
            start_id: int = UNDEFINED_INDEX
    ) -> None:
        (
            self.below_event_from_shaped_result, self.contour_id,
            self.from_first_operand, self.from_in_to_out,
            self.from_shaped_result, self.id, self.interior_to_left,
            self.other_interior_to_left, self.overlap_kind, self.right,
            self.start, self.start_id
        ) = (
            below_event_from_shaped_result, contour_id, from_first_operand,
            from_in_to_out, from_shaped_result, id_, interior_to_left,
            other_interior_to_left, overlap_kind, right, start, start_id
        )

    __repr__ = recursive_repr()(generate_repr(__init__,
                                              field_seeker=seekers.complex_))

    @property
    def end_id(self) -> int:
        return self.opposite.start_id

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
                point, self.right, self.from_first_operand,
                self.interior_to_left
        )
        self.right = RightShapedEvent(point, self)
        return tail


LeftShapedEvent = TypeVar('LeftShapedEvent', LeftHolelessEvent, LeftHoleyEvent)


class RightShapedEvent(RightEvent):
    __slots__ = 'id', 'start', 'start_id'

    def __init__(self,
                 start: Point,
                 left: LeftShapedEvent,
                 *,
                 id_: int = UNDEFINED_INDEX,
                 start_id: int = UNDEFINED_INDEX) -> None:
        self.id, self.left, self.start, self.start_id = (
            id_, left, start, start_id
        )

    __repr__ = recursive_repr()(generate_repr(__init__,
                                              field_seeker=seekers.complex_))

    @property
    def end_id(self) -> int:
        return self.opposite.start_id

    @property
    def from_first_operand(self) -> bool:
        return self.left.from_first_operand

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
        left_start_index = index
        while index < events_count and events[index].start == current_start:
            index += 1
        left_stop_index = index - 1
        has_right_events = left_start_index >= right_start_index + 1
        has_left_events = left_stop_index >= left_start_index
        if has_right_events:
            result[right_start_index:left_start_index - 1] = range(
                    right_start_index + 1, left_start_index - 1 + 1
            )
            result[left_start_index - 1] = (left_stop_index
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
