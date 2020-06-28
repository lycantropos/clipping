from typing import (Iterable,
                    List,
                    Sequence)

from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)
from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from clipping.hints import (Contour,
                            Multipolygon,
                            Multisegment,
                            Point,
                            Polygon,
                            Segment)
from .hints import BoundingBox
from .utils import (contour_to_segments,
                    flatten)


def from_points(points: Iterable[Point]) -> BoundingBox:
    """
    Builds bounding box from points.
    """
    points = iter(points)
    x_min, y_min = x_max, y_max = next(points)
    for x, y in points:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def from_multisegment(multisegment: Multisegment) -> BoundingBox:
    """
    Builds bounding box from multisegment.
    """
    return from_points(flatten(multisegment))


def from_multipolygon(multipolygon: Multipolygon) -> BoundingBox:
    """
    Builds bounding box from multipolygon.
    """
    return from_points(flatten(border for border, _ in multipolygon))


def disjoint_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes do not intersect.

    >>> disjoint_with((0, 2, 0, 2), (0, 2, 0, 2))
    False
    >>> disjoint_with((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> disjoint_with((0, 2, 0, 2), (2, 4, 0, 2))
    False
    >>> disjoint_with((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> disjoint_with((0, 2, 0, 2), (2, 4, 3, 5))
    True
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min)


def intersects_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect.

    >>> intersects_with((0, 2, 0, 2), (0, 2, 0, 2))
    True
    >>> intersects_with((0, 2, 0, 2), (1, 3, 1, 3))
    True
    >>> intersects_with((0, 2, 0, 2), (2, 4, 0, 2))
    True
    >>> intersects_with((0, 2, 0, 2), (2, 4, 2, 4))
    True
    >>> intersects_with((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (right_x_min <= left_x_max and left_x_min <= right_x_max
            and right_y_min <= left_y_max and left_y_min <= right_y_max)


def coupled_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect in some region or by the edge.

    >>> coupled_with((0, 2, 0, 2), (0, 2, 0, 2))
    True
    >>> coupled_with((0, 2, 0, 2), (1, 3, 1, 3))
    True
    >>> coupled_with((0, 2, 0, 2), (2, 4, 0, 2))
    True
    >>> coupled_with((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> coupled_with((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    return (intersects_with(left, right)
            and (not touches_with(left, right)
                 or edges_overlap_with(left, right)))


def touches_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect at point or by the edge.

    >>> touches_with((0, 2, 0, 2), (0, 2, 0, 2))
    False
    >>> touches_with((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> touches_with((0, 2, 0, 2), (2, 4, 0, 2))
    True
    >>> touches_with((0, 2, 0, 2), (2, 4, 2, 4))
    True
    >>> touches_with((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return ((left_x_min == right_x_max or left_x_max == right_x_min)
            and (left_y_min <= right_y_max and right_y_min <= left_y_max)
            or (left_x_min <= right_x_max and right_x_min <= left_x_max)
            and (left_y_min == right_y_max or right_y_min == left_y_max))


def edges_overlap_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect by the edge.

    >>> edges_overlap_with((0, 2, 0, 2), (0, 2, 0, 2))
    False
    >>> edges_overlap_with((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> edges_overlap_with((0, 2, 0, 2), (2, 4, 0, 2))
    True
    >>> edges_overlap_with((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> edges_overlap_with((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return ((left_x_min == right_x_max or left_x_max == right_x_min)
            and (left_y_min < right_y_max and right_y_min < left_y_max)
            or (left_x_min < right_x_max and right_x_min < left_x_max)
            and (left_y_min == right_y_max or right_y_min == left_y_max))


def is_subset_of(test: BoundingBox, goal: BoundingBox) -> bool:
    """
    Checks if the bounding box is the subset of the other.

    >>> is_subset_of((0, 2, 0, 2), (0, 2, 0, 2))
    True
    >>> is_subset_of((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 0, 2))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    test_x_min, test_x_max, test_y_min, test_y_max = test
    goal_x_min, goal_x_max, goal_y_min, goal_y_max = goal
    return (goal_x_min <= test_x_min and test_x_max <= goal_x_max
            and goal_y_min <= test_y_min and test_y_max <= goal_y_max)


def within_of(test: BoundingBox, goal: BoundingBox) -> bool:
    """
    Checks if the bounding box is contained in an interior of the other.

    >>> within_of((0, 2, 0, 2), (0, 2, 0, 2))
    False
    >>> within_of((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> within_of((0, 2, 0, 2), (2, 4, 0, 2))
    False
    >>> within_of((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> within_of((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    test_x_min, test_x_max, test_y_min, test_y_max = test
    goal_x_min, goal_x_max, goal_y_min, goal_y_max = goal
    return (goal_x_min < test_x_min and test_x_max < goal_x_max
            and goal_y_min < test_y_min and test_y_max < goal_y_max)


def intersects_with_segment(bounding_box: BoundingBox,
                            segment: Segment) -> bool:
    """
    Checks if the bounding box intersects the segment.
    """
    segment_bounding_box = from_points(segment)
    return (intersects_with(segment_bounding_box, bounding_box)
            and (is_subset_of(segment_bounding_box, bounding_box)
                 or any(segments_relationship(edge, segment)
                        is not SegmentsRelationship.NONE
                        for edge in to_segments(bounding_box))))


def coupled_with_segment(bounding_box: BoundingBox,
                         segment: Segment) -> bool:
    """
    Checks if the bounding box intersects the segment at more than one point.
    """
    segment_bounding_box = from_points(segment)
    return (coupled_with(segment_bounding_box, bounding_box)
            and (is_subset_of(segment_bounding_box, bounding_box)
                 or any(segments_relationship(edge, segment)
                        not in (SegmentsRelationship.TOUCH,
                                SegmentsRelationship.NONE)
                        for edge in to_segments(bounding_box))))


def is_subset_of_region(bounding_box: BoundingBox, border: Contour) -> bool:
    """
    Checks if the bounding box is the subset of the region.
    """
    return all(segment_in_region(segment, border) in (Relation.COMPONENT,
                                                      Relation.ENCLOSED,
                                                      Relation.WITHIN)
               for segment in to_segments(bounding_box))


def within_of_region(bounding_box: BoundingBox, border: Contour) -> bool:
    """
    Checks if the bounding box is contained in an interior of the region.
    """
    return (all(point_in_region(vertex, border) is Relation.WITHIN
                for vertex in to_vertices(bounding_box))
            and all(segments_relationship(edge, border_edge)
                    is SegmentsRelationship.NONE
                    for edge in to_segments(bounding_box)
                    for border_edge in contour_to_segments(border)))


def is_subset_of_multiregion(bounding_box: BoundingBox,
                             borders: List[Contour]) -> bool:
    """
    Checks if the bounding box is the subset of the multiregion.
    """
    return any(is_subset_of(bounding_box, from_points(border))
               and is_subset_of_region(bounding_box, border)
               for border in borders)


def intersects_with_polygon(bounding_box: BoundingBox,
                            polygon: Polygon) -> bool:
    """
    Checks if the bounding box intersects the polygon.
    """
    border, holes = polygon
    polygon_bounding_box = from_points(border)
    if not intersects_with(polygon_bounding_box, bounding_box):
        return False
    elif (is_subset_of(polygon_bounding_box, bounding_box)
          or any(contains_point(bounding_box, vertex)
                 for vertex in border)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(bounding_box)]
    if (within_of(bounding_box, polygon_bounding_box)
            and all(relation is Relation.WITHIN for relation in relations)
            and all(segments_relationship(edge, border_edge)
                    is SegmentsRelationship.NONE
                    for edge in to_segments(bounding_box)
                    for border_edge in contour_to_segments(border))):
        return not any(within_of(bounding_box, from_points(hole))
                       and within_of_region(bounding_box, hole)
                       for hole in holes)
    else:
        return (any(relation is not Relation.DISJOINT
                    for relation in relations)
                or any(intersects_with_segment(bounding_box, border_edge)
                       for border_edge in contour_to_segments(border)))


def coupled_with_polygon(bounding_box: BoundingBox, polygon: Polygon) -> bool:
    """
    Checks if the bounding box intersects the polygon in some region
    or by the edge.
    """
    border, holes = polygon
    polygon_bounding_box = from_points(border)
    if not coupled_with(polygon_bounding_box, bounding_box):
        return False
    elif (is_subset_of(polygon_bounding_box, bounding_box)
          or any(covers_point(bounding_box, vertex)
                 for vertex in border)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(bounding_box)]
    if any(relation is Relation.WITHIN for relation in relations):
        return (not all(relation is Relation.WITHIN for relation in relations)
                or not is_subset_of_multiregion(bounding_box, holes))
    else:
        return (not is_subset_of_multiregion(bounding_box, holes)
                if (is_subset_of(bounding_box, polygon_bounding_box)
                    and is_subset_of_region(bounding_box, border))
                else any(segment_in_contour(segment, border)
                         is Relation.OVERLAP
                         or segment_in_region(segment, border)
                         in (Relation.CROSS, Relation.COMPONENT,
                             Relation.ENCLOSED)
                         for segment in to_segments(bounding_box)))


def contains_point(bounding_box: BoundingBox, point: Point) -> bool:
    x_min, x_max, y_min, y_max = bounding_box
    x, y = point
    return x_min <= x <= x_max and y_min <= y <= y_max


def covers_point(bounding_box: BoundingBox, point: Point) -> bool:
    x_min, x_max, y_min, y_max = bounding_box
    x, y = point
    return x_min < x < x_max and y_min < y < y_max


def to_vertices(bounding_box: BoundingBox) -> Sequence[Point]:
    x_min, x_max, y_min, y_max = bounding_box
    return (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)


def to_segments(bounding_box: BoundingBox) -> Sequence[Segment]:
    x_min, x_max, y_min, y_max = bounding_box
    return (((x_min, y_min), (x_max, y_min)),
            ((x_max, y_min), (x_max, y_max)),
            ((x_min, y_max), (x_max, y_max)),
            ((x_min, y_min), (x_min, y_max)))


def to_intersecting_segments(bounding_box: BoundingBox,
                             multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if intersects_with_segment(bounding_box, segment)]


def to_coupled_segments(bounding_box: BoundingBox,
                        multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if coupled_with_segment(bounding_box, segment)]


def to_intersecting_polygons(bounding_box: BoundingBox,
                             multipolygon: Multipolygon) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if intersects_with_polygon(bounding_box, polygon)]


def to_coupled_polygons(bounding_box: BoundingBox,
                        multipolygon: Multipolygon) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if coupled_with_polygon(bounding_box, polygon)]
