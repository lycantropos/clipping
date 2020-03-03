from reprlib import recursive_repr
from typing import Optional

from reprit.base import generate_repr
from robust.linear import segments_intersection

from clipping.hints import (Coordinate,
                            Point,
                            Segment)
from .enums import EdgeType


class Event:
    __slots__ = ('is_right_endpoint', 'start', 'complement', 'from_left',
                 'edge_type', 'in_out', 'other_in_out', 'in_result',
                 'result_in_out', 'position', 'contour_id',
                 'below_in_result_event')

    def __init__(self,
                 is_right_endpoint: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_left: bool,
                 edge_type: EdgeType,
                 in_out: bool = False,
                 other_in_out: bool = False,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: Optional[int] = None,
                 below_in_result_event: Optional['Event'] = None) -> None:
        self.is_right_endpoint = is_right_endpoint
        self.start = start
        self.complement = complement
        self.from_left = from_left
        self.edge_type = edge_type
        self.in_out = in_out
        self.other_in_out = other_in_out
        self.in_result = in_result
        self.result_in_out = result_in_out
        self.position = position
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

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
    def is_horizontal(self) -> bool:
        _, start_y = self.start
        _, end_y = self.end
        return start_y == end_y

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def y_at(self, x: Coordinate) -> Coordinate:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            start_x, start_y = self.start
            if x == start_x:
                return start_y
            end_x, end_y = self.end
            if x == end_x:
                return end_y
            _, result = segments_intersection(self.segment,
                                              ((x, start_y), (x, end_y)))
            return result
