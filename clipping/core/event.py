from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (Optional,
                    Sequence,
                    Tuple)

from ground.hints import Point
from reprit.base import generate_repr

from .enums import OverlapKind
from .hints import SegmentEndpoints


class Event(ABC):
    complement = None  # type: Optional[Event]

    __slots__ = ()

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    @abstractmethod
    def start(self) -> Point:
        """Returns start of the event."""

    @property
    @abstractmethod
    def is_left(self) -> bool:
        """Checks if the event's start corresponds to the leftmost endpoint."""

    @property
    def is_vertical(self) -> bool:
        return self.start.x == self.end.x

    @property
    def primary(self) -> Optional['BinaryEvent']:
        return self if self.is_left else self.complement

    @abstractmethod
    def divide(self, point: Point) -> 'Event':
        """Divides the event at given break point and returns tail."""


class NaryEvent(Event):
    @classmethod
    def from_segment_endpoints(cls, segment_endpoints: SegmentEndpoints
                               ) -> 'NaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        result = cls(True, start, None)
        result.complement = cls(False, end, result)
        return result

    __slots__ = 'complement', '_is_left', '_start'

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['Event']) -> None:
        self._is_left = is_left
        self._start = start
        self.complement = complement

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, break_point: Point) -> 'NaryEvent':
        tail = self.complement.complement = NaryEvent(True, break_point,
                                                      self.complement)
        self.complement = NaryEvent(False, break_point, self)
        return tail


class BinaryEvent(Event):
    @classmethod
    def from_segment_endpoints(cls,
                               segment_endpoints: SegmentEndpoints,
                               from_left: bool) -> 'BinaryEvent':
        start, end = segment_endpoints
        if start > end:
            start, end = end, start
        event = cls(True, start, None, from_left)
        event.complement = cls(False, end, event, from_left)
        return event

    __slots__ = 'complement', 'from_left', '_is_left', '_start'

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_left: bool) -> None:
        self._is_left = is_left
        self._start = start
        self.complement = complement
        self.from_left = from_left

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'BinaryEvent':
        tail = self.complement.complement = BinaryEvent(
                True, point, self.complement, self.from_left)
        self.complement = BinaryEvent(False, point, self, self.from_left)
        return tail


class OrientedEvent(Event):
    @classmethod
    def from_endpoints(cls,
                       segment_endpoints: SegmentEndpoints,
                       from_left: bool) -> 'OrientedEvent':
        start, end = segment_endpoints
        inside_on_left = True
        if start > end:
            start, end = end, start
            inside_on_left = False
        event = cls(True, start, None, from_left, inside_on_left)
        event.complement = cls(False, end, event, from_left, inside_on_left)
        return event

    __slots__ = ('complement', 'from_left', 'in_result', 'interior_to_left',
                 'other_interior_to_left', 'overlap_kind',
                 'position', '_is_left', '_start')

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['OrientedEvent'],
                 from_left: bool,
                 interior_to_left: bool) -> None:
        self._is_left = is_left
        self._start = start
        self.complement = complement
        self.from_left = from_left
        self.interior_to_left = interior_to_left

    @property
    def is_left(self) -> bool:
        return self._is_left

    @property
    def start(self) -> Point:
        return self._start

    def divide(self, point: Point) -> 'OrientedEvent':
        tail = self.complement.complement = type(self)(
                True, point, self.complement, self.from_left,
                self.interior_to_left)
        self.complement = type(self)(False, point, self, self.from_left,
                                     self.interior_to_left)
        return tail


class MixedEvent(OrientedEvent):
    __slots__ = ('other_interior_to_left', 'is_overlap', '_is_left',
                 'in_result')

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['MixedEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 is_overlap: bool = False,
                 in_result: bool = False) -> None:
        super().__init__(is_left, start, complement, from_left,
                         interior_to_left)
        self.other_interior_to_left = other_interior_to_left
        self.is_overlap = is_overlap
        self.in_result = in_result

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return not self.other_interior_to_left and not self.is_overlap


class ShapedEvent(OrientedEvent):
    __slots__ = ('in_result', '_is_left', 'other_interior_to_left',
                 'overlap_kind', 'position')

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['ShapedEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 position: int = 0) -> None:
        super().__init__(is_left, start, complement, from_left,
                         interior_to_left)
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
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)


class HoleyEvent(ShapedEvent):
    __slots__ = 'below_in_result_event', 'contour_id', 'result_in_out'

    def __init__(self,
                 is_left: bool,
                 start: Point,
                 complement: Optional['HoleyEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: Optional[int] = None,
                 below_in_result_event: Optional['HoleyEvent'] = None) -> None:
        super().__init__(is_left, start, complement, from_left,
                         interior_to_left, other_interior_to_left,
                         overlap_kind, in_result, position)
        self.result_in_out = result_in_out
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

    __repr__ = recursive_repr()(generate_repr(__init__))


def events_to_connectivity(events: Sequence[BinaryEvent]) -> Sequence[int]:
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
