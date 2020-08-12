from typing import (Iterator,
                    List,
                    Optional,
                    Tuple)

from reprit.base import generate_repr

from wagyu.hints import Coordinate, Point
from .bounding_box import BoundingBox
from .edge import Edge
from .enums import PointInPolygonResult
from .utils import (are_floats_almost_equal,
                    are_floats_greater_than_or_equal,
                    is_float_almost_zero)


class PointNode:
    __slots__ = 'x', 'y', 'prev', 'next', 'ring'

    def __init__(self, x: Coordinate, y: Coordinate) -> None:
        from .ring import Ring
        self.x = x
        self.y = y
        self.prev = self  # type: PointNode
        self.next = self  # type: PointNode
        self.ring = None  # type: Optional[Ring]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'PointNode') -> bool:
        return (self.x == other.x and self.y == other.y
                if isinstance(other, PointNode)
                else ((self.x, self.y) == other
                      if isinstance(other, tuple)
                      else NotImplemented))

    def __iter__(self) -> Iterator['PointNode']:
        cursor = self
        while True:
            yield cursor
            cursor = cursor.next
            if cursor is self:
                break

    def __lt__(self, other: 'PointNode') -> bool:
        if self.y != other.y:
            return other.y < self.y
        elif other.x != self.x:
            return other.x > self.x
        else:
            return other.ring.depth < self.ring.depth

    def __reversed__(self) -> Iterator['PointNode']:
        cursor = self
        while True:
            yield cursor
            cursor = cursor.prev
            if cursor is self:
                break

    @classmethod
    def from_point(cls, point: Point) -> 'PointNode':
        return cls(*point)

    @property
    def bottom_node(self) -> 'PointNode':
        dups = None
        node = self
        cursor = node.next
        while cursor is not node:
            if cursor.y > node.y:
                node = cursor
                dups = None
            elif cursor.y == node.y and cursor.x <= node.x:
                if cursor.x < node.x:
                    dups = None
                    node = cursor
                else:
                    if cursor.next is not node and cursor.prev is node:
                        dups = cursor
            cursor = cursor.next
        if dups is not None:
            # there appears to be at least 2 vertices at bottom point
            while dups is not cursor:
                if not cursor.is_bottom_to(dups):
                    node = dups
                dups = dups.next
                while dups != node:
                    dups = dups.next
        return node

    @property
    def stats(self) -> Tuple[float, int, BoundingBox]:
        area = size = 0
        min_x = max_x = self.x
        min_y = max_y = self.y
        cursor = self
        while True:
            size += 1
            if cursor.x > max_x:
                max_x = cursor.x
            elif cursor.x < min_x:
                min_x = cursor.x
            if cursor.y > max_y:
                max_y = cursor.y
            elif cursor.y < min_y:
                min_y = cursor.y
            area += (cursor.prev.x + cursor.x) * (cursor.prev.y - cursor.y)
            cursor = cursor.next
            if cursor is self:
                break
        return area / 2, size, (min_x, max_x, min_y, max_y)

    def is_bottom_to(self, other: 'PointNode') -> bool:
        node = self.prev
        while node == self and node is not self:
            node = node.prev
        dx1p = abs(get_points_slope(self, node))
        node = self.next
        while node == self and node is not self:
            node = node.next
        dx1n = abs(get_points_slope(self, node))
        node = other.prev
        while node == other and node is not other:
            node = node.prev
        dx2p = abs(get_points_slope(other, node))
        node = other.next
        while node == other and node is not other:
            node = node.next
        dx2n = abs(get_points_slope(other, node))
        if (are_floats_almost_equal(max(dx1p, dx1n), max(dx2p, dx2n))
                and are_floats_almost_equal(min(dx1p, dx1n), min(dx2p, dx2n))):
            area, *_ = self.stats
            return area > 0.0  # if otherwise identical use orientation
        else:
            return ((are_floats_greater_than_or_equal(dx1p, dx2p)
                     and are_floats_greater_than_or_equal(dx1p, dx2n))
                    or (are_floats_greater_than_or_equal(dx1n, dx2p)
                        and are_floats_greater_than_or_equal(dx1n, dx2n)))

    def reverse(self) -> None:
        for node in self:
            node.next, node.prev = node.prev, node.next

    def place_before(self, other: 'PointNode') -> None:
        self.next, self.prev = other, other.prev
        self.prev.next = other.prev = self


def get_points_slope(left: PointNode, right: PointNode) -> float:
    return Edge(point_node_to_point(left), point_node_to_point(right)).slope


def point_node_to_point(node: PointNode) -> Point:
    return node.x, node.y


def maybe_point_node_to_points(node: Optional[PointNode]) -> List[Point]:
    return [] if node is None else [point_node_to_point(sub_node)
                                    for sub_node in node]


def node_key(node: PointNode) -> Tuple[Coordinate, Coordinate]:
    return -node.y, node.x


def point_in_polygon(pt: PointNode, op: PointNode) -> PointInPolygonResult:
    result = PointInPolygonResult.OUTSIDE
    start_op = op
    pt_x, pt_y = pt.x, pt.y
    while True:
        if op.next.y == pt_y and (op.next.x == pt_x or op.y == pt_y
                                  and ((op.next.x > pt_x) is (op.x < pt_x))):
            return PointInPolygonResult.ON
        if (op.y < pt_y) is not (op.next.y < pt_y):
            if op.x >= pt_x:
                if op.next.x > pt_x:
                    # switch between point outside polygon
                    # and point inside polygon
                    result = (PointInPolygonResult.INSIDE
                              if result is PointInPolygonResult.OUTSIDE
                              else PointInPolygonResult.OUTSIDE)
                else:
                    d = ((op.x - pt_x) * (op.next.y - pt_y)
                         - (op.next.x - pt_x) * (op.y - pt_y))
                    if is_float_almost_zero(d):
                        return PointInPolygonResult.ON
                    if (d > 0) is (op.next.y > op.y):
                        result = (PointInPolygonResult.INSIDE
                                  if result is PointInPolygonResult.OUTSIDE
                                  else PointInPolygonResult.OUTSIDE)
            elif op.next.x > pt_x:
                d = ((op.x - pt_x) * (op.next.y - pt_y)
                     - (op.next.x - pt_x) * (op.y - pt_y))
                if is_float_almost_zero(d):
                    return PointInPolygonResult.ON
                if (d > 0) is (op.next.y > op.y):
                    result = (PointInPolygonResult.INSIDE
                              if result is PointInPolygonResult.OUTSIDE
                              else PointInPolygonResult.OUTSIDE)
        op = op.next
        if op is start_op:
            break
    return result


def inside_or_outside_special(first_polygon: PointNode,
                              other_polygon: PointNode
                              ) -> PointInPolygonResult:
    # we are going to loop through all the points of the original triangle,
    # the goal is to find a convex edge that with its next and previous
    # forms a triangle with its centroid that is within the first ring,
    # then we will check the other polygon to see if it is within this polygon
    cursor = first_polygon
    while True:
        if is_convex(cursor):
            centroid = points_centroid(cursor)
            if (point_in_polygon(centroid, first_polygon)
                    is PointInPolygonResult.INSIDE):
                return point_in_polygon(centroid, other_polygon)
        cursor = cursor.next
        if cursor is first_polygon:
            break
    raise RuntimeError('Could not find a point within the polygon to test')


def is_convex(node: PointNode) -> bool:
    area = node.ring.area
    prev_node = node.prev
    next_node = node.next
    delta_x = node.x - prev_node.x
    delta_y = node.y - prev_node.y
    next_delta_x = next_node.x - node.x
    next_delta_y = next_node.y - node.y
    cross = delta_x * next_delta_y - next_delta_x * delta_y
    return cross < 0 < area or cross > 0 > area


def points_centroid(node: PointNode) -> Point:
    prev_node = node.prev
    next_node = node.next
    return ((prev_node.x + node.x + next_node.x) / 3,
            (prev_node.y + node.y + next_node.y) / 3)


def has_collinear_edge(first_node: PointNode, second_node: PointNode) -> bool:
    # it is assumed pt_a and pt_b are at the same location
    return (first_node.next == second_node.prev
            or second_node.next == first_node.prev)


def find_start_and_end_of_collinear_edges(pt_a: PointNode,
                                          pt_b: PointNode
                                          ) -> Tuple[PointNode, PointNode,
                                                     PointNode, PointNode]:
    # search backward on A, forwards on B first
    same_ring = pt_a.ring is pt_b.ring
    back = pt_a
    forward = pt_b
    first = True
    while True:
        while back.prev == back and back is not forward:
            back = back.prev
            if back is pt_a:
                break
        if back is forward:
            back = back.prev
            forward = forward.next
            break
        while forward.next == forward and back is not forward:
            forward = forward.next
            if forward is pt_b:
                break
        if not first and (back is pt_a or forward is pt_b):
            break
        if back is forward:
            back = back.prev
            forward = forward.next
            break
        back = back.prev
        forward = forward.next
        first = False
        if back != forward:
            break
    start_a = back.next
    # if there are repeated points at the diverge
    # we want to select only the first of those repeated points
    while not same_ring and start_a == start_a.next and start_a is not pt_a:
        start_a = start_a.next
    end_b = forward.prev
    while not same_ring and end_b == end_b.prev and end_b is not pt_b:
        end_b = end_b.prev
    # search backward on B, forwards on A next
    back = pt_b
    forward = pt_a
    first = True
    while True:
        while back.prev == back and back is not forward:
            back = back.prev
            if back is pt_b:
                break
        if back is forward:
            back = back.prev
            forward = forward.next
            break
        while forward.next == forward and back is not forward:
            forward = forward.next
            if forward is pt_a:
                break
        if not first and (back is pt_b or forward is pt_a):
            break
        if (back is forward
                or first is None and (back is end_b or forward is start_a)):
            back = back.prev
            forward = forward.next
            break
        back = back.prev
        forward = forward.next
        first = False
        if back != forward:
            break
    start_b = back.next
    while not same_ring and start_b == start_b.next and start_b is not pt_b:
        start_b = start_b.next
    end_a = forward.prev
    while not same_ring and end_a == end_a.prev and end_a is not pt_a:
        end_a = end_a.prev
    return start_a, end_a, start_b, end_b


def fix_collinear_path(path: Tuple[PointNode, PointNode, PointNode, PointNode]
                       ) -> Tuple[Optional[PointNode], Optional[PointNode]]:
    # Left and right are just the opposite ends of the
    # collinear path, they may not be actually left
    # and right of each other.
    # The left end is start_1 and end_2
    # The right end is start_2 and end_1

    # NOTE spike detection is checking that the
    # pointers are the same values, not position!
    # additionally duplicate points we will treat
    # if they are a spike left.
    start_1, end_1, start_2, end_2 = path
    spike_left = start_1 is end_2
    spike_right = start_2 is end_1

    if spike_left and spike_right:
        # If both ends are spikes we should simply
        # delete all the points. (they should be in a loop)
        itr = start_1
        while itr is not None:
            itr.prev.next = None
            itr.prev = None
            itr.ring = None
            itr = itr.next
        return None, None
    elif spike_left:
        prev = start_2.prev
        itr = start_2
        while itr is not end_1:
            itr.prev.next = None
            itr.prev = None
            itr.ring = None
            itr = itr.next
        prev.next = end_1
        end_1.prev = prev
        return end_1, None
    elif spike_right:
        prev = start_1.prev
        itr = start_1
        while itr is not end_2:
            itr.prev.next = None
            itr.prev = None
            itr.ring = None
            itr = itr.next
        prev.next = end_2
        end_2.prev = prev
        return end_2, None
    else:
        prev_1 = start_1.prev
        prev_2 = start_2.prev
        itr = start_1
        while True:
            itr.prev.next = None
            itr.prev = None
            itr.ring = None
            itr = itr.next
            if itr is end_1 or itr is None:
                break
        itr = start_2
        while True:
            itr.prev.next = None
            itr.prev = None
            itr.ring = None
            itr = itr.next
            if itr is end_2 or itr is None:
                break
        if start_1 is end_1 and start_2 is end_2:
            return None, None
        elif start_1 is end_1:
            prev_2.next = end_2
            end_2.prev = prev_2
            return end_2, None
        elif start_2 is end_2:
            prev_1.next = end_1
            end_1.prev = prev_1
            return end_1, None
        else:
            prev_1.next = end_2
            end_2.prev = prev_1
            prev_2.next = end_1
            end_1.prev = prev_2
            return end_1, end_2
