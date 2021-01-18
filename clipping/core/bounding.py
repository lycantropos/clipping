from typing import (Iterable,
                    List,
                    Sequence)

from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)

from .hints import (Box,
                    Contour,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
                    Point,
                    Polygon,
                    Region,
                    Segment)
from .utils import (SegmentsRelation,
                    contour_to_segments,
                    flatten,
                    segments_relation)


def from_points(points: Iterable[Point]) -> Box:
    """
    Builds box from points.
    """
    points = iter(points)
    x_min, y_min = x_max, y_max = next(points)
    for x, y in points:
        if x < x_min:
            x_min = x
        elif x > x_max:
            x_max = x
        if y < y_min:
            y_min = y
        elif y > y_max:
            y_max = y
    return x_min, x_max, y_min, y_max


def from_multisegment(multisegment: Multisegment) -> Box:
    """
    Builds box from multisegment.
    """
    return from_points(flatten(multisegment))


def from_multipolygon(multipolygon: Multipolygon) -> Box:
    """
    Builds box from multipolygon.
    """
    return from_points(flatten(border for border, _ in multipolygon))


def from_multiregion(multiregion: Multiregion) -> Box:
    """
    Builds box from multiregion.
    """
    return from_points(flatten(multiregion))


def disjoint_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes do not intersect.

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


def intersects_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect.

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


def coupled_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect in some region or by the edge.

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


def touches_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect at point or by the edge.

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


def edges_overlap_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect by the edge.

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


def is_subset_of(test: Box, goal: Box) -> bool:
    """
    Checks if the box is the subset of the other.

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


def within_of(test: Box, goal: Box) -> bool:
    """
    Checks if the box is contained in an interior of the other.

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


def intersects_with_segment(box: Box,
                            segment: Segment) -> bool:
    """
    Checks if the box intersects the segment.
    """
    segment_box = from_points(segment)
    return (intersects_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(segments_relation(edge, segment)
                        is not SegmentsRelation.DISJOINT
                        for edge in to_segments(box))))


def coupled_with_segment(box: Box,
                         segment: Segment) -> bool:
    """
    Checks if the box intersects the segment at more than one point.
    """
    segment_box = from_points(segment)
    return (coupled_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(segments_relation(edge, segment)
                        not in (SegmentsRelation.TOUCH,
                                SegmentsRelation.DISJOINT)
                        for edge in to_segments(box))))


def is_subset_of_region(box: Box, border: Contour) -> bool:
    """
    Checks if the box is the subset of the region.
    """
    return all(segment_in_region(segment, border) in (Relation.COMPONENT,
                                                      Relation.ENCLOSED,
                                                      Relation.WITHIN)
               for segment in to_segments(box))


def within_of_region(box: Box, border: Contour) -> bool:
    """
    Checks if the box is contained in an interior of the region.
    """
    return (all(point_in_region(vertex, border) is Relation.WITHIN
                for vertex in to_vertices(box))
            and all(segments_relation(edge, border_edge)
                    is SegmentsRelation.DISJOINT
                    for edge in to_segments(box)
                    for border_edge in contour_to_segments(border)))


def is_subset_of_multiregion(box: Box,
                             borders: List[Contour]) -> bool:
    """
    Checks if the box is the subset of the multiregion.
    """
    return any(is_subset_of(box, from_points(border))
               and is_subset_of_region(box, border)
               for border in borders)


def intersects_with_polygon(box: Box,
                            polygon: Polygon) -> bool:
    """
    Checks if the box intersects the polygon.
    """
    border, holes = polygon
    polygon_box = from_points(border)
    if not intersects_with(polygon_box, box):
        return False
    elif (is_subset_of(polygon_box, box)
          or any(contains_point(box, vertex) for vertex in border)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(box)]
    if (within_of(box, polygon_box)
            and all(relation is Relation.WITHIN for relation in relations)
            and all(segments_relation(edge, border_edge)
                    is SegmentsRelation.DISJOINT
                    for edge in to_segments(box)
                    for border_edge in contour_to_segments(border))):
        return not any(within_of(box, from_points(hole))
                       and within_of_region(box, hole)
                       for hole in holes)
    else:
        return (any(relation is not Relation.DISJOINT
                    for relation in relations)
                or any(intersects_with_segment(box, border_edge)
                       for border_edge in contour_to_segments(border)))


def intersects_with_region(box: Box,
                           region: Region) -> bool:
    """
    Checks if the box intersects the region.
    """
    region_box = from_points(region)
    return (intersects_with(region_box, box)
            and (is_subset_of(region_box, box)
                 or any(contains_point(box, vertex) for vertex in region)
                 or any(point_in_region(vertex, region)
                        is not Relation.DISJOINT
                        for vertex in to_vertices(box))
                 or any(intersects_with_segment(box, border_edge)
                        for border_edge in contour_to_segments(region))))


def coupled_with_polygon(box: Box, polygon: Polygon) -> bool:
    """
    Checks if the box intersects the polygon in continuous points set.
    """
    border, holes = polygon
    polygon_box = from_points(border)
    if not coupled_with(polygon_box, box):
        return False
    elif (is_subset_of(polygon_box, box)
          or any(covers_point(box, vertex)
                 for vertex in border)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(box)]
    if any(relation is Relation.WITHIN for relation in relations):
        return (not all(relation is Relation.WITHIN for relation in relations)
                or not is_subset_of_multiregion(box, holes))
    else:
        return (not is_subset_of_multiregion(box, holes)
                if (is_subset_of(box, polygon_box)
                    and is_subset_of_region(box, border))
                else any(segment_in_contour(segment, border)
                         is Relation.OVERLAP
                         or segment_in_region(segment, border)
                         in (Relation.CROSS, Relation.COMPONENT,
                             Relation.ENCLOSED)
                         for segment in to_segments(box)))


def coupled_with_region(box: Box, region: Region) -> bool:
    """
    Checks if the box intersects the region in continuous points set.
    """
    region_box = from_points(region)
    if not coupled_with(region_box, box):
        return False
    elif (is_subset_of(region_box, box)
          or any(covers_point(box, vertex)
                 for vertex in region)):
        return True
    return (any(point_in_region(vertex, region) is Relation.WITHIN
                for vertex in to_vertices(box))
            or is_subset_of(box, region_box)
            and is_subset_of_region(box, region)
            or any(segment_in_contour(segment, region)
                   is Relation.OVERLAP
                   or segment_in_region(segment, region)
                   in (Relation.CROSS, Relation.COMPONENT,
                       Relation.ENCLOSED)
                   for segment in to_segments(box)))


def contains_point(box: Box, point: Point) -> bool:
    x_min, x_max, y_min, y_max = box
    x, y = point
    return x_min <= x <= x_max and y_min <= y <= y_max


def covers_point(box: Box, point: Point) -> bool:
    x_min, x_max, y_min, y_max = box
    x, y = point
    return x_min < x < x_max and y_min < y < y_max


def to_vertices(box: Box) -> Sequence[Point]:
    x_min, x_max, y_min, y_max = box
    return (x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)


def to_segments(box: Box) -> Sequence[Segment]:
    x_min, x_max, y_min, y_max = box
    return (((x_min, y_min), (x_max, y_min)),
            ((x_max, y_min), (x_max, y_max)),
            ((x_min, y_max), (x_max, y_max)),
            ((x_min, y_min), (x_min, y_max)))


def to_intersecting_segments(box: Box,
                             multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if intersects_with_segment(box, segment)]


def to_coupled_segments(box: Box,
                        multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if coupled_with_segment(box, segment)]


def to_intersecting_polygons(box: Box,
                             multipolygon: Multipolygon) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if intersects_with_polygon(box, polygon)]


def to_intersecting_regions(box: Box,
                            multiregion: Multiregion) -> Multiregion:
    return [region
            for region in multiregion
            if intersects_with_region(box, region)]


def to_coupled_polygons(box: Box,
                        multipolygon: Multipolygon) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if coupled_with_polygon(box, polygon)]


def to_coupled_regions(box: Box,
                       multiregion: Multiregion) -> Multiregion:
    return [region
            for region in multiregion
            if coupled_with_region(box, region)]
