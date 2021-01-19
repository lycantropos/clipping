from reprlib import recursive_repr
from typing import (Optional,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.hints import Point
from reprit.base import generate_repr

from .enums import OverlapKind


class NaryEvent:
    __slots__ = 'is_right_endpoint', 'start', 'complement'

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['Event']) -> None:
        self.is_right_endpoint = is_right_endpoint
        self.start = start
        self.complement = complement

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start


class BinaryEvent:
    __slots__ = 'is_right_endpoint', 'start', 'complement', 'from_left'

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_left: bool) -> None:
        self.is_right_endpoint = is_right_endpoint
        self.start = start
        self.complement = complement
        self.from_left = from_left

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def is_vertical(self) -> bool:
        return self.start.x == self.end.x

    @property
    def primary(self) -> Optional['BinaryEvent']:
        return self.complement if self.is_right_endpoint else self


class MixedEvent(BinaryEvent):
    __slots__ = ('interior_to_left', 'other_interior_to_left', 'is_overlap',
                 'in_result')

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['MixedEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 is_overlap: bool = False,
                 in_result: bool = False) -> None:
        super().__init__(is_right_endpoint, start, complement, from_left)
        self.interior_to_left = interior_to_left
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


class ShapedEvent(BinaryEvent):
    __slots__ = ('interior_to_left', 'other_interior_to_left', 'overlap_kind',
                 'in_result', 'position')

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['ShapedEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 position: int = 0) -> None:
        super().__init__(is_right_endpoint, start, complement, from_left)
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
    def outside(self) -> bool:
        """
        Checks if the segment touches or disjoint with the intersection.
        """
        return (not self.other_interior_to_left
                and self.overlap_kind is OverlapKind.NONE)


class HoleyEvent(ShapedEvent):
    __slots__ = ('interior_to_left', 'other_interior_to_left', 'overlap_kind',
                 'in_result', 'result_in_out', 'position', 'contour_id',
                 'below_in_result_event')

    def __init__(self,
                 is_right_endpoint: bool,
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
        super().__init__(is_right_endpoint, start, complement, from_left,
                         interior_to_left, other_interior_to_left,
                         overlap_kind, in_result, position)
        self.result_in_out = result_in_out
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

    __repr__ = recursive_repr()(generate_repr(__init__))


Event = TypeVar('Event', NaryEvent, BinaryEvent, MixedEvent, ShapedEvent,
                HoleyEvent)


def events_to_connectivity(events: Sequence[BinaryEvent]) -> Sequence[int]:
    events_count = len(events)
    result = [0] * events_count
    index = 0
    while index < events_count:
        current_start = events[index].start
        right_start_index = index
        while (index < events_count
               and events[index].start == current_start
               and events[index].is_right_endpoint):
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
