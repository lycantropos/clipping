from reprlib import recursive_repr
from typing import (Optional,
                    TypeVar)

from reprit.base import generate_repr

from clipping.hints import (Point,
                            Segment)
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

    @property
    def segment(self) -> Segment:
        return self.start, self.end


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
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def segment(self) -> Segment:
        return self.start, self.end


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
                 'in_result', 'result_in_out', 'position', 'contour_id',
                 'below_in_result_event')

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['ShapedEvent'],
                 from_left: bool,
                 interior_to_left: bool,
                 other_interior_to_left: bool = False,
                 overlap_kind: OverlapKind = OverlapKind.NONE,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: Optional[int] = None,
                 below_in_result_event: Optional['ShapedEvent'] = None
                 ) -> None:
        super().__init__(is_right_endpoint, start, complement, from_left)
        self.interior_to_left = interior_to_left
        self.other_interior_to_left = other_interior_to_left
        self.overlap_kind = overlap_kind
        self.in_result = in_result
        self.result_in_out = result_in_out
        self.position = position
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
    def is_common_region_boundary(self) -> bool:
        """
        Checks if the segment is a boundary of intersection's region.
        """
        return self.overlap_kind is OverlapKind.SAME_ORIENTATION

    @property
    def is_common_polyline_component(self) -> bool:
        """
        Checks if the segment is a component of intersection's polyline.
        """
        return self.overlap_kind is OverlapKind.DIFFERENT_ORIENTATION

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


Event = TypeVar('Event', NaryEvent, BinaryEvent, MixedEvent, ShapedEvent)
