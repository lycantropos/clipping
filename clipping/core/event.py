from reprlib import recursive_repr
from typing import (Optional,
                    TypeVar)

from reprit.base import generate_repr

from clipping.hints import (Point,
                            Segment)
from .enums import EdgeType


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
    __slots__ = 'in_out', 'other_in_out', 'overlaps', 'in_result'

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['MixedEvent'],
                 from_left: bool,
                 in_out: bool = False,
                 other_in_out: bool = False,
                 overlaps: bool = False,
                 in_result: bool = False) -> None:
        super().__init__(is_right_endpoint, start, complement, from_left)
        self.in_out = in_out
        self.other_in_out = other_in_out
        self.overlaps = overlaps
        self.in_result = in_result

    __repr__ = recursive_repr()(generate_repr(__init__))


class ShapedEvent(BinaryEvent):
    __slots__ = ('edge_type', 'in_out', 'other_in_out', 'in_result',
                 'result_in_out', 'position', 'contour_id',
                 'below_in_result_event')

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['ShapedEvent'],
                 from_left: bool,
                 edge_type: EdgeType = EdgeType.NORMAL,
                 in_out: bool = False,
                 other_in_out: bool = False,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: Optional[int] = None,
                 below_in_result_event: Optional['ShapedEvent'] = None
                 ) -> None:
        super().__init__(is_right_endpoint, start, complement, from_left)
        self.edge_type = edge_type
        self.in_out = in_out
        self.other_in_out = other_in_out
        self.in_result = in_result
        self.result_in_out = result_in_out
        self.position = position
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

    __repr__ = recursive_repr()(generate_repr(__init__))


Event = TypeVar('Event', NaryEvent, BinaryEvent, MixedEvent, ShapedEvent)
