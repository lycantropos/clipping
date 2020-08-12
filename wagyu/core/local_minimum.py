from itertools import (chain,
                       repeat)
from typing import (Iterable,
                    List,
                    Optional)

from reprit.base import generate_repr

from wagyu.hints import (Contour,
                         Coordinate,
                         Multipolygon,
                         Polygon)
from .bound import (Bound,
                    to_bound_towards_maximum,
                    to_bound_towards_minimum)
from .contour import (contour_to_edges)
from .edge import Edge
from .enums import (EdgeSide,
                    OperandKind)
from .utils import (flatten,
                    rotate_sequence)


class LocalMinimum:
    __slots__ = 'left_bound', 'right_bound', 'y', 'minimum_has_horizontal'

    def __init__(self,
                 left_bound: Bound,
                 right_bound: Bound,
                 y: float,
                 minimum_has_horizontal: bool) -> None:
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.y = y
        self.minimum_has_horizontal = minimum_has_horizontal

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'LocalMinimum') -> bool:
        return (self.left_bound == other.left_bound
                and self.right_bound == other.right_bound
                and self.y == other.y
                and self.minimum_has_horizontal is other.minimum_has_horizontal
                if isinstance(other, LocalMinimum)
                else NotImplemented)

    def __lt__(self, other: 'LocalMinimum') -> bool:
        return ((self.y, self.minimum_has_horizontal)
                < (other.y, other.minimum_has_horizontal)
                if isinstance(other, LocalMinimum)
                else NotImplemented)

    def initialize(self) -> None:
        left_bound = self.left_bound
        if left_bound.edges:
            left_bound.current_edge_index = 0
            left_bound.next_edge_index = 1
            left_bound.current_x = float(left_bound.current_edge.bottom_x)
            left_bound.winding_count = left_bound.opposite_winding_count = 0
            left_bound.side = EdgeSide.LEFT
            left_bound.ring = None
        right_bound = self.right_bound
        if right_bound.edges:
            right_bound.current_edge_index = 0
            right_bound.next_edge_index = 1
            right_bound.current_x = float(right_bound.current_edge.bottom_x)
            right_bound.winding_count = right_bound.opposite_winding_count = 0
            right_bound.side = EdgeSide.RIGHT
            right_bound.ring = None


def multipolygon_to_local_minimums(multipolygon: Multipolygon,
                                   operand_kind: OperandKind
                                   ) -> List[LocalMinimum]:
    return list(flatten(map(polygon_to_local_minimums, multipolygon,
                            repeat(operand_kind))))


def polygon_to_local_minimums(polygon: Polygon,
                              operand_kind: OperandKind) -> List[LocalMinimum]:
    border, holes = polygon
    return list(chain(contour_to_local_minimums(border, operand_kind),
                      flatten(map(contour_to_local_minimums, holes,
                                  repeat(operand_kind)))))


def contour_to_local_minimums(contour: Contour,
                              operand_kind: OperandKind) -> List[LocalMinimum]:
    return list(_contour_to_local_minimums(contour, operand_kind))


def _contour_to_local_minimums(contour: Contour,
                               operand_kind: OperandKind
                               ) -> Iterable[LocalMinimum]:
    edges = contour_to_edges(contour)
    if not edges:
        return
    edges = to_edges_starting_on_local_maximum(edges)
    first_minimum = last_maximum = None  # type: Optional[Bound]
    while edges:
        to_min_bound = to_bound_towards_minimum(edges)
        assert edges, 'Edges is empty after only creating a single bound.'
        to_max_bound = to_bound_towards_maximum(edges)
        to_min_bound.fix_horizontals()
        to_max_bound.fix_horizontals()
        to_max_bound_edges = to_max_bound.edges
        to_min_bound_edges = to_min_bound.edges
        to_max_non_horizontal_index = to_first_non_horizontal_index(
                to_max_bound_edges)
        to_min_non_horizontal_index = to_first_non_horizontal_index(
                to_min_bound_edges)
        minimum_has_horizontal = (to_max_non_horizontal_index > 0
                                  or to_min_non_horizontal_index > 0)
        if minimum_has_horizontal:
            if (to_max_bound_edges[to_max_non_horizontal_index].bottom_x
                    > to_min_bound_edges[
                        to_min_non_horizontal_index].bottom_x):
                minimum_is_left = True
                to_min_bound.move_horizontals(to_max_bound)
            else:
                minimum_is_left = False
                to_max_bound.move_horizontals(to_min_bound)
        else:
            minimum_is_left = (
                    to_max_bound_edges[to_max_non_horizontal_index].slope
                    <= to_min_bound_edges[to_min_non_horizontal_index].slope)
        if last_maximum is not None:
            to_min_bound.maximum_bound = last_maximum
        to_max_bound.operand_kind = to_min_bound.operand_kind = operand_kind
        min_front = to_min_bound_edges[0]
        if not minimum_is_left:
            to_min_bound.side = EdgeSide.RIGHT
            to_max_bound.side = EdgeSide.LEFT
            to_min_bound.winding_delta = -1
            to_max_bound.winding_delta = 1
            minimum = LocalMinimum(to_max_bound, to_min_bound,
                                   min_front.bottom_y, minimum_has_horizontal)
            if last_maximum is None:
                first_minimum = minimum.right_bound
            else:
                last_maximum.maximum_bound = minimum.right_bound
            last_maximum = minimum.left_bound
        else:
            to_min_bound.side = EdgeSide.LEFT
            to_max_bound.side = EdgeSide.RIGHT
            to_min_bound.winding_delta = -1
            to_max_bound.winding_delta = 1
            minimum = LocalMinimum(to_min_bound, to_max_bound,
                                   min_front.bottom_y, minimum_has_horizontal)
            if last_maximum is None:
                first_minimum = minimum.left_bound
            else:
                last_maximum.maximum_bound = minimum.left_bound
            last_maximum = minimum.right_bound
        yield minimum
    last_maximum.maximum_bound = first_minimum
    first_minimum.maximum_bound = last_maximum


def to_first_non_horizontal_index(edges: List[Edge]) -> int:
    return next(index
                for index, edge in enumerate(edges)
                if not edge.is_horizontal)


def to_scanbeams(local_minimums: List[LocalMinimum]) -> List[Coordinate]:
    return sorted(value.y for value in local_minimums)


def to_edges_starting_on_local_maximum(edges: List[Edge]) -> List[Edge]:
    return (rotate_sequence(edges, to_local_maximum_index(edges))
            if len(edges) > 2
            else edges)


def to_local_maximum_index(edges: List[Edge]) -> int:
    prev_edge = edges[-1]
    prev_edge_is_horizontal = prev_edge.is_horizontal
    y_decreasing_before_last_horizontal = False
    for index, edge in enumerate(edges):
        edge_is_horizontal = edge.is_horizontal
        if (not prev_edge_is_horizontal and not edge_is_horizontal
                and edge.top == prev_edge.top):
            break
        if not edge_is_horizontal and prev_edge_is_horizontal:
            if (y_decreasing_before_last_horizontal
                    and (edge.top == prev_edge.bottom
                         or edge.top == prev_edge.top)):
                break
        elif (not y_decreasing_before_last_horizontal
              and not prev_edge_is_horizontal and edge_is_horizontal
              and (prev_edge.top == edge.top or prev_edge.top == edge.bottom)):
            y_decreasing_before_last_horizontal = True
        prev_edge, prev_edge_is_horizontal = edge, edge_is_horizontal
    else:
        index = len(edges)
    return index
