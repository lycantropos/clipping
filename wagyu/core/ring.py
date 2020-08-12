import math
from typing import (List,
                    Optional)

from reprit.base import generate_repr

from wagyu.hints import Point
from .bounding_box import (BoundingBox,
                           is_subset_of)
from .enums import PointInPolygonResult
from .point_node import (PointNode,
                         inside_or_outside_special,
                         maybe_point_node_to_points,
                         node_key,
                         point_in_polygon)


class Ring:
    __slots__ = ('index', 'parent', 'children', 'node', 'bottom_node',
                 'corrected', 'box', '_area', '_size', '_is_hole')

    def __init__(self,
                 index: int = 0,
                 children: Optional[List[Optional['Ring']]] = None,
                 points: Optional[List[Point]] = None,
                 corrected: bool = False) -> None:
        self.index = index
        self.parent = None  # type: Optional[Ring]
        self.children = children or []
        self.node = (None
                     if not points
                     else node_from_ring_points(points, self))
        self.bottom_node = None  # type: Optional[PointNode]
        self.corrected = corrected
        self.box = (0, 0, 0, 0)  # type: BoundingBox
        self._area = math.nan  # type: float
        self._is_hole = False  # type: bool
        self._size = 0  # type: int

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'Ring') -> bool:
        return (self.index == other.index
                and self.children == other.children
                and self.node == other.node
                and self.bottom_node == other.bottom_node
                and self.corrected is other.corrected
                if isinstance(other, Ring)
                else NotImplemented)

    def __lt__(self, other: 'Ring') -> bool:
        return ((self.node is not None
                 if self.node is None or other.node is None
                 else abs(self.area) < abs(other.area))
                if isinstance(other, Ring)
                else NotImplemented)

    @property
    def area(self) -> float:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._area

    @property
    def depth(self) -> int:
        result = 0
        cursor = self.parent
        while cursor is not None:
            result += 1
            cursor = cursor.parent
        return result

    @property
    def is_hole(self) -> bool:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._is_hole

    @property
    def points(self) -> List[Point]:
        return maybe_point_node_to_points(self.node)

    @property
    def bottom_points(self) -> List[Point]:
        return maybe_point_node_to_points(self.bottom_node)

    @property
    def size(self) -> int:
        if math.isnan(self._area):
            self.recalculate_stats()
        return self._size

    @property
    def sorted_nodes(self) -> List[PointNode]:
        return sorted(self.node,
                      key=node_key)

    def get_lowermost_ring(self, other: 'Ring') -> 'Ring':
        # work out which polygon fragment has the correct hole state ...
        if self.bottom_node is None:
            self.bottom_node = self.node.bottom_node
        if other.bottom_node is None:
            other.bottom_node = other.node.bottom_node
        bottom_node = self.bottom_node
        other_bottom_node = other.bottom_node
        if bottom_node.y > other_bottom_node.y:
            return self
        elif bottom_node.y < other_bottom_node.y:
            return other
        elif bottom_node.x < other_bottom_node.x:
            return self
        elif bottom_node.x > other_bottom_node.x:
            return other
        elif bottom_node.next is bottom_node:
            return other
        elif other_bottom_node.next is other_bottom_node:
            return self
        elif bottom_node.is_bottom_to(other_bottom_node):
            return self
        else:
            return other

    def is_subset_of(self, other: 'Ring') -> bool:
        if not is_subset_of(self.box, other.box):
            return False
        if abs(other.area) < abs(self.area):
            return False
        first_out_node = self.node.next
        second_out_node = other.node.next
        cursor = first_out_node
        while True:
            result = point_in_polygon(cursor, second_out_node)
            if result is not PointInPolygonResult.ON:
                return result is PointInPolygonResult.INSIDE
            cursor = cursor.next
            if cursor is first_out_node:
                break
        result = inside_or_outside_special(first_out_node, second_out_node)
        return result is PointInPolygonResult.INSIDE

    def is_descendant_of(self, other: 'Ring') -> bool:
        cursor = self.parent
        while cursor is not None:
            if cursor is other:
                return True
            cursor = cursor.parent
        return False

    def recalculate_stats(self) -> None:
        if self.node is not None:
            self._area, self._size, self.box = self.node.stats
            self._is_hole = self._area <= 0.0

    def reset_stats(self) -> None:
        self._area = math.nan
        self._size = 0
        self.box = (0, 0, 0, 0)
        self._is_hole = False

    def set_stats(self, area: float, size: int, box: BoundingBox) -> None:
        self._area, self._size, self.box, self._is_hole = (area, size, box,
                                                           area <= 0.)

    def update_points(self) -> None:
        for node in self.node:
            node.ring = self


def node_from_ring_points(points: List[Point], ring: Ring) -> PointNode:
    points = reversed(points)
    result = PointNode.from_point(next(points))
    result.ring = ring
    for point in points:
        node = PointNode.from_point(point)
        node.ring = ring
        node.place_before(result)
        result = node
    return result


def remove_from_children(ring: Ring, children: List[Optional[Ring]]) -> None:
    for index, candidate in enumerate(children):
        if candidate is ring:
            children[index] = None
            return


def set_to_children(ring: Ring, children: List[Optional[Ring]]) -> None:
    for index, child in enumerate(children):
        if child is None:
            children[index] = ring
            return
    children.append(ring)
