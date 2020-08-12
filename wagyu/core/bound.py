from typing import (List,
                    Optional)

from reprit.base import generate_repr

from wagyu.hints import (Coordinate,
                         Point)
from .edge import (Edge,
                   are_edges_slopes_equal)
from .enums import (EdgeSide,
                    Fill,
                    OperandKind,
                    OperationKind)
from .ring import Ring
from .utils import insort_unique


class Bound:
    __slots__ = ('edges', '_current_edge_index', '_next_edge_index',
                 'last_point', 'ring', 'current_x', 'position',
                 'winding_count', 'opposite_winding_count', 'winding_delta',
                 'operand_kind', 'side', 'maximum_bound')

    def __init__(self,
                 edges: Optional[List[Edge]] = None,
                 current_edge_index: Optional[int] = None,
                 next_edge_index: Optional[int] = None,
                 last_point: Optional[Point] = None,
                 ring: Optional[Ring] = None,
                 current_x: float = 0.,
                 position: int = 0,
                 winding_count: int = 0,
                 opposite_winding_count: int = 0,
                 winding_delta: int = 0,
                 operand_kind: OperandKind = OperandKind.SUBJECT,
                 side: EdgeSide = EdgeSide.LEFT) -> None:
        self.edges = edges or []
        self._current_edge_index = (
            None
            if (current_edge_index is None
                or current_edge_index >= len(self.edges))
            else current_edge_index)
        self._next_edge_index = (None
                                 if (next_edge_index is None
                                     or next_edge_index >= len(self.edges))
                                 else next_edge_index)
        self.last_point = (0, 0) if last_point is None else last_point
        self.ring = ring
        self.current_x = current_x
        self.position = position
        self.winding_count = winding_count
        self.opposite_winding_count = opposite_winding_count
        self.winding_delta = winding_delta
        self.operand_kind = operand_kind
        self.side = side
        self.maximum_bound = None  # type: Optional[Bound]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Bound') -> bool:
        return (self.edges == other.edges
                and self.current_edge_index == other.current_edge_index
                and self.next_edge_index == other.next_edge_index
                and self.last_point == other.last_point
                and self.ring == other.ring
                and self.current_x == other.current_x
                and self.position == other.position
                and self.winding_count == other.winding_count
                and self.opposite_winding_count == other.opposite_winding_count
                and self.winding_delta == other.winding_delta
                and self.operand_kind is other.operand_kind
                and self.side is other.side
                if isinstance(other, Bound)
                else NotImplemented)

    @property
    def current_edge(self) -> Edge:
        return self.edges[self.current_edge_index]

    @property
    def next_edge(self) -> Edge:
        return self.edges[self.next_edge_index]

    @property
    def current_edge_index(self) -> int:
        return (len(self.edges)
                if self._current_edge_index is None
                else self._current_edge_index)

    @property
    def next_edge_index(self) -> int:
        return (len(self.edges)
                if self._next_edge_index is None
                else self._next_edge_index)

    @current_edge_index.setter
    def current_edge_index(self, value: int) -> None:
        self._current_edge_index = value if value < len(self.edges) else None

    @next_edge_index.setter
    def next_edge_index(self, value: int) -> None:
        self._next_edge_index = value if value < len(self.edges) else None

    def is_contributing(self,
                        operation_kind: OperationKind,
                        subject_fill: Fill,
                        clip_fill: Fill) -> bool:
        fill, other_fill = ((subject_fill, clip_fill)
                            if self.operand_kind is OperandKind.SUBJECT
                            else (clip_fill, subject_fill))
        if fill is Fill.NON_ZERO:
            if abs(self.winding_count) != 1:
                return False
        elif fill is Fill.POSITIVE:
            if self.winding_count != 1:
                return False
        elif fill is Fill.NEGATIVE:
            if self.winding_count != -1:
                return False
        if operation_kind is OperationKind.INTERSECTION:
            if other_fill is Fill.EVEN_ODD or other_fill is Fill.NON_ZERO:
                return self.opposite_winding_count != 0
            elif other_fill is Fill.POSITIVE:
                return self.opposite_winding_count > 0
            else:
                return self.opposite_winding_count < 0
        elif operation_kind is OperationKind.UNION:
            if other_fill is Fill.EVEN_ODD or other_fill is Fill.NON_ZERO:
                return self.opposite_winding_count == 0
            elif other_fill is Fill.POSITIVE:
                return self.opposite_winding_count <= 0
            else:
                return self.opposite_winding_count >= 0
        elif operation_kind is OperationKind.DIFFERENCE:
            if self.operand_kind is OperandKind.SUBJECT:
                if other_fill is Fill.EVEN_ODD or other_fill is Fill.NON_ZERO:
                    return self.opposite_winding_count == 0
                elif other_fill is Fill.POSITIVE:
                    return self.opposite_winding_count <= 0
                else:
                    return self.opposite_winding_count >= 0
            else:
                if other_fill is Fill.EVEN_ODD or other_fill is Fill.NON_ZERO:
                    return self.opposite_winding_count != 0
                elif other_fill is Fill.POSITIVE:
                    return self.opposite_winding_count > 0
                else:
                    return self.opposite_winding_count < 0
        else:
            return True

    def is_even_odd_fill(self,
                         subject_fill: Fill,
                         clip_fill: Fill) -> bool:
        if self.operand_kind is OperandKind.SUBJECT:
            return subject_fill is Fill.EVEN_ODD
        else:
            return clip_fill is Fill.EVEN_ODD

    def is_even_odd_other_fill(self,
                               subject_fill: Fill,
                               clip_fill: Fill) -> bool:
        if self.operand_kind is OperandKind.SUBJECT:
            return clip_fill is Fill.EVEN_ODD
        else:
            return subject_fill is Fill.EVEN_ODD

    def is_intermediate(self, y: Coordinate) -> bool:
        return (self.next_edge_index < len(self.edges)
                and self.current_edge.top_y == y)

    def is_maxima(self, y: Coordinate) -> bool:
        return (self.next_edge_index == len(self.edges)
                and self.current_edge.top_y == y)

    def fix_horizontals(self) -> None:
        edge_index = 0
        next_index = 1
        edges = self.edges
        if next_index == len(edges):
            return
        edge = edges[edge_index]
        if edge.is_horizontal and edges[next_index].bottom != edge.top:
            edge.reverse_horizontal()
        prev_edge = edge
        edge_index += 1
        while edge_index < len(edges):
            edge = edges[edge_index]
            if edge.is_horizontal and prev_edge.top != edge.bottom:
                edge.reverse_horizontal()
            prev_edge = edge
            edge_index += 1

    def move_horizontals(self, other: 'Bound') -> None:
        index = 0
        edges = self.edges
        while index < len(edges):
            edge = edges[index]
            if not edge.is_horizontal:
                break
            edge.reverse_horizontal()
            index += 1
        if not index:
            return
        other_edges = other.edges
        other_edges.extend(reversed(edges[:index]))
        del edges[:index]
        other_edges[:] = other_edges[-index:] + other_edges[:-index]

    def to_next_edge(self, scanbeams: List[Coordinate]) -> None:
        self.current_edge_index += 1
        if self.current_edge_index < len(self.edges):
            self.next_edge_index += 1
            self.current_x = self.current_edge.bottom_x
            if not self.current_edge.is_horizontal:
                insort_unique(scanbeams, self.current_edge.top_y)


def to_bound_towards_maximum(edges: List[Edge]) -> Bound:
    edges_iterator = iter(edges)
    edge = next(edges_iterator)
    edge_is_horizontal = edge.is_horizontal
    y_decreasing_before_last_horizontal = False
    for next_edge_index, next_edge in enumerate(edges_iterator,
                                                start=1):
        next_edge_is_horizontal = next_edge.is_horizontal
        if (not next_edge_is_horizontal and not edge_is_horizontal
                and edge.top == next_edge.top):
            break
        if not next_edge_is_horizontal and edge_is_horizontal:
            if (y_decreasing_before_last_horizontal
                    and (next_edge.top == edge.bottom
                         or next_edge.top == edge.top)):
                break
        elif (not y_decreasing_before_last_horizontal
              and not edge_is_horizontal and next_edge_is_horizontal
              and (edge.top == next_edge.top or edge.top == next_edge.bottom)):
            y_decreasing_before_last_horizontal = True
        edge, edge_is_horizontal = next_edge, next_edge_is_horizontal
        next_edge_index += 1
    else:
        next_edge_index = len(edges)
    result = Bound(edges[:next_edge_index])
    del edges[:next_edge_index]
    return result


def to_bound_towards_minimum(edges: List[Edge]) -> Bound:
    edges_iterator = iter(edges)
    edge = next(edges_iterator)
    edge_is_horizontal = edge.is_horizontal
    if edge_is_horizontal:
        edge.reverse_horizontal()
    y_increasing_before_last_horizontal = False
    for next_edge_index, next_edge in enumerate(edges_iterator,
                                                start=1):
        next_edge_is_horizontal = next_edge.is_horizontal
        if (not next_edge_is_horizontal and not edge_is_horizontal
                and edge.bottom == next_edge.bottom):
            break
        if not next_edge_is_horizontal and edge_is_horizontal:
            if (y_increasing_before_last_horizontal
                    and (next_edge.bottom == edge.bottom
                         or next_edge.bottom == edge.top)):
                break
        elif (not y_increasing_before_last_horizontal
              and not edge_is_horizontal and next_edge_is_horizontal
              and (edge.bottom == next_edge.top
                   or edge.bottom == next_edge.bottom)):
            y_increasing_before_last_horizontal = True
        edge_is_horizontal, edge = next_edge_is_horizontal, next_edge
        if edge_is_horizontal:
            edge.reverse_horizontal()
    else:
        next_edge_index = len(edges)
    result = Bound(edges[next_edge_index - 1::-1])
    del edges[:next_edge_index]
    return result


def intersection_compare(left: Bound, right: Bound) -> bool:
    return (left.current_x <= right.current_x
            or are_edges_slopes_equal(left.current_edge, right.current_edge))
