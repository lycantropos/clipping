from typing import (List,
                    Tuple)

from reprit.base import generate_repr

from .bound import (Bound,
                    intersection_compare)
from .bubble_sort import bubble_sort
from .utils import are_floats_almost_equal
from ..hints import Point


class IntersectNode:
    __slots__ = 'first_bound', 'second_bound', 'point'

    def __init__(self,
                 first_bound: Bound,
                 second_bound: Bound,
                 point: Point) -> None:
        self.first_bound = first_bound
        self.second_bound = second_bound
        self.point = point

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'IntersectNode') -> bool:
        return (self.first_bound == other.first_bound
                and self.second_bound == other.second_bound
                and self.point == other.point
                if isinstance(other, IntersectNode)
                else NotImplemented)

    def __lt__(self, other: 'IntersectNode') -> bool:
        _, point_y = self.point
        _, other_point_y = other.point
        return ((self.first_bound.opposite_winding_count
                 + self.second_bound.opposite_winding_count) <
                (other.first_bound.opposite_winding_count
                 + other.second_bound.opposite_winding_count)
                if are_floats_almost_equal(float(point_y),
                                           float(other_point_y))
                else other_point_y < point_y)

    def has_bound(self, bound: Bound) -> bool:
        return self.first_bound is bound or self.second_bound is bound


def build_intersect_list(active_bounds: List[Bound]
                         ) -> Tuple[List[Bound], List[IntersectNode]]:
    intersections = []

    def on_swap(left: Bound, right: Bound) -> None:
        intersection = left.current_edge & right.current_edge
        if intersection is None:
            raise RuntimeError('Trying to find intersection of lines '
                               'that do not intersect')
        intersections.append(IntersectNode(left, right, intersection))

    return (bubble_sort(active_bounds, intersection_compare, on_swap),
            intersections)
