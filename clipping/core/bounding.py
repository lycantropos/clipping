from typing import (Iterable,
                    Sequence)

from ground.base import Context
from ground.hints import (Contour,
                          Point,
                          Segment)
from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)

from .hints import (Box,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
                    Polygon,
                    Region,
                    SegmentEndpoints)
from .utils import (SegmentsRelation,
                    contour_to_edges_endpoints,
                    flatten,
                    segments_relation)


def from_contour(contour: Contour) -> Box:
    """
    Builds box from contour.
    """
    return from_points(contour.vertices)


def from_multisegment(multisegment: Multisegment) -> Box:
    """
    Builds box from multisegment.
    """
    return from_points(flatten((segment.start, segment.end)
                               for segment in multisegment))


def from_multipolygon(multipolygon: Multipolygon) -> Box:
    """
    Builds box from multipolygon.
    """
    return from_points(flatten(border.vertices for border, _ in multipolygon))


def from_multiregion(multiregion: Multiregion) -> Box:
    """
    Builds box from multiregion.
    """
    return from_points(flatten(region.vertices for region in multiregion))


def from_points(points: Iterable[Point]) -> Box:
    """
    Builds box from points.
    """
    points = iter(points)
    point = next(points)
    x_min, y_min = x_max, y_max = point.x, point.y
    for point in points:
        x, y = point.x, point.y
        if x < x_min:
            x_min = x
        elif x > x_max:
            x_max = x
        if y < y_min:
            y_min = y
        elif y > y_max:
            y_max = y
    return x_min, x_max, y_min, y_max


def from_segment(segment: Segment) -> Box:
    """
    Builds box from segment.
    """
    return from_points((segment.start, segment.end))


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
    return (right_x_max < left_x_min or left_x_max < right_x_min
            or right_y_max < left_y_min or left_y_max < right_y_min)


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
                            start: Point,
                            end: Point,
                            *,
                            context: Context) -> bool:
    """
    Checks if the box intersects the segment.
    """
    segment_box = from_points((start, end))
    return (intersects_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(segments_relation(edge_start, edge_end, start, end)
                        is not SegmentsRelation.DISJOINT
                        for edge_start, edge_end
                        in to_edges_endpoints(box,
                                              context=context))))


def coupled_with_segment(box: Box,
                         segment: Segment,
                         *,
                         context: Context) -> bool:
    """
    Checks if the box intersects the segment at more than one point.
    """
    segment_box = from_segment(segment)
    return (coupled_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(segments_relation(edge_start, edge_end, segment.start,
                                          segment.end)
                        not in (SegmentsRelation.TOUCH,
                                SegmentsRelation.DISJOINT)
                        for edge_start, edge_end
                        in to_edges_endpoints(box,
                                              context=context))))


def is_subset_of_region(box: Box,
                        border: Contour,
                        *,
                        context: Context) -> bool:
    """
    Checks if the box is the subset of the region.
    """
    return all(segment_in_region(segment, border) in (Relation.COMPONENT,
                                                      Relation.ENCLOSED,
                                                      Relation.WITHIN)
               for segment in to_edges(box,
                                       context=context))


def within_of_region(box: Box,
                     border: Contour,
                     *,
                     context: Context) -> bool:
    """
    Checks if the box is contained in an interior of the region.
    """
    return (all(point_in_region(vertex, border) is Relation.WITHIN
                for vertex in to_vertices(box,
                                          context=context))
            and all(segments_relation(edge_start, edge_end, border_edge_start,
                                      border_edge_end)
                    is SegmentsRelation.DISJOINT
                    for edge_start, edge_end
                    in to_edges_endpoints(box,
                                          context=context)
                    for border_edge_start, border_edge_end
                    in contour_to_edges_endpoints(border)))


def is_subset_of_multiregion(box: Box,
                             multiregion: Multiregion,
                             *,
                             context: Context) -> bool:
    """
    Checks if the box is the subset of the multiregion.
    """
    return any(is_subset_of(box, from_contour(region))
               and is_subset_of_region(box, region,
                                       context=context)
               for region in multiregion)


def intersects_with_polygon(box: Box,
                            polygon: Polygon,
                            *,
                            context: Context) -> bool:
    """
    Checks if the box intersects the polygon.
    """
    border, holes = polygon
    polygon_box = from_contour(border)
    if not intersects_with(polygon_box, box):
        return False
    elif (is_subset_of(polygon_box, box)
          or any(contains_point(box, vertex) for vertex in border.vertices)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(box,
                                           context=context)]
    if (within_of(box, polygon_box)
            and all(relation is Relation.WITHIN for relation in relations)
            and all(segments_relation(edge_start, edge_end, border_edge_start,
                                      border_edge_end)
                    is SegmentsRelation.DISJOINT
                    for edge_start, edge_end
                    in to_edges_endpoints(box,
                                          context=context)
                    for border_edge_start, border_edge_end
                    in contour_to_edges_endpoints(border))):
        return not any(within_of(box, from_contour(hole))
                       and within_of_region(box, hole,
                                            context=context)
                       for hole in holes)
    else:
        return (any(relation is not Relation.DISJOINT
                    for relation in relations)
                or any(intersects_with_segment(box, border_edge_start,
                                               border_edge_end,
                                               context=context)
                       for border_edge_start, border_edge_end
                       in contour_to_edges_endpoints(border)))


def intersects_with_region(box: Box,
                           region: Region,
                           *,
                           context: Context) -> bool:
    """
    Checks if the box intersects the region.
    """
    region_box = from_contour(region)
    return (intersects_with(region_box, box)
            and (is_subset_of(region_box, box)
                 or any(contains_point(box, vertex)
                        for vertex in region.vertices)
                 or any(point_in_region(vertex, region)
                        is not Relation.DISJOINT
                        for vertex in to_vertices(box,
                                                  context=context))
                 or any(intersects_with_segment(box, border_edge_start,
                                                border_edge_end,
                                                context=context)
                        for border_edge_start, border_edge_end in
                        contour_to_edges_endpoints(region))))


def coupled_with_polygon(box: Box,
                         polygon: Polygon,
                         *,
                         context: Context) -> bool:
    """
    Checks if the box intersects the polygon in continuous points set.
    """
    border, holes = polygon
    polygon_box = from_contour(border)
    if not coupled_with(polygon_box, box):
        return False
    elif (is_subset_of(polygon_box, box)
          or any(covers_point(box, vertex) for vertex in border.vertices)):
        return True
    relations = [point_in_region(vertex, border)
                 for vertex in to_vertices(box,
                                           context=context)]
    if any(relation is Relation.WITHIN for relation in relations):
        return (not all(relation is Relation.WITHIN for relation in relations)
                or not is_subset_of_multiregion(box, holes,
                                                context=context))
    else:
        return (not is_subset_of_multiregion(box, holes,
                                             context=context)
                if (is_subset_of(box, polygon_box)
                    and is_subset_of_region(box, border,
                                            context=context))
                else any(segment_in_contour(segment, border)
                         is Relation.OVERLAP
                         or segment_in_region(segment, border)
                         in (Relation.CROSS, Relation.COMPONENT,
                             Relation.ENCLOSED)
                         for segment in to_edges(box,
                                                 context=context)))


def coupled_with_region(box: Box,
                        region: Region,
                        *,
                        context: Context) -> bool:
    """
    Checks if the box intersects the region in continuous points set.
    """
    region_box = from_contour(region)
    if not coupled_with(region_box, box):
        return False
    elif (is_subset_of(region_box, box)
          or any(covers_point(box, vertex) for vertex in region.vertices)):
        return True
    return (any(point_in_region(vertex, region) is Relation.WITHIN
                for vertex in to_vertices(box,
                                          context=context))
            or is_subset_of(box, region_box)
            and is_subset_of_region(box, region,
                                    context=context)
            or any(segment_in_contour(segment, region)
                   is Relation.OVERLAP
                   or segment_in_region(segment, region)
                   in (Relation.CROSS, Relation.COMPONENT,
                       Relation.ENCLOSED)
                   for segment in to_edges(box,
                                           context=context)))


def contains_point(box: Box, point: Point) -> bool:
    x_min, x_max, y_min, y_max = box
    return x_min <= point.x <= x_max and y_min <= point.y <= y_max


def covers_point(box: Box, point: Point) -> bool:
    x_min, x_max, y_min, y_max = box
    return x_min < point.x < x_max and y_min < point.y < y_max


def to_vertices(box: Box,
                *,
                context: Context) -> Sequence[Point]:
    x_min, x_max, y_min, y_max = box
    point_cls = context.point_cls
    return (point_cls(x_min, y_min), point_cls(x_max, y_min),
            point_cls(x_max, y_max), point_cls(x_min, y_max))


def to_edges_endpoints(box: Box,
                       *,
                       context: Context) -> Sequence[SegmentEndpoints]:
    x_min, x_max, y_min, y_max = box
    point_cls = context.point_cls
    return ((point_cls(x_min, y_min), point_cls(x_max, y_min)),
            (point_cls(x_max, y_min), point_cls(x_max, y_max)),
            (point_cls(x_min, y_max), point_cls(x_max, y_max)),
            (point_cls(x_min, y_min), point_cls(x_min, y_max)))


def to_edges(box: Box,
             *,
             context: Context) -> Sequence[Segment]:
    x_min, x_max, y_min, y_max = box
    point_cls, segment_cls = context.point_cls, context.segment_cls
    return (segment_cls(point_cls(x_min, y_min), point_cls(x_max, y_min)),
            segment_cls(point_cls(x_max, y_min), point_cls(x_max, y_max)),
            segment_cls(point_cls(x_min, y_max), point_cls(x_max, y_max)),
            segment_cls(point_cls(x_min, y_min), point_cls(x_min, y_max)))


def to_intersecting_segments(box: Box,
                             multisegment: Multisegment,
                             *,
                             context: Context) -> Multisegment:
    return [segment
            for segment in multisegment
            if intersects_with_segment(box, segment.start, segment.end,
                                       context=context)]


def to_coupled_segments(box: Box,
                        multisegment: Multisegment,
                        *,
                        context: Context) -> Multisegment:
    return [segment
            for segment in multisegment
            if coupled_with_segment(box, segment,
                                    context=context)]


def to_intersecting_polygons(box: Box,
                             multipolygon: Multipolygon,
                             *,
                             context: Context) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if intersects_with_polygon(box, polygon,
                                       context=context)]


def to_intersecting_regions(box: Box,
                            multiregion: Multiregion,
                            *,
                            context: Context) -> Multiregion:
    return [region
            for region in multiregion
            if intersects_with_region(box, region,
                                      context=context)]


def to_coupled_polygons(box: Box,
                        multipolygon: Multipolygon,
                        *,
                        context: Context) -> Multipolygon:
    return [polygon
            for polygon in multipolygon
            if coupled_with_polygon(box, polygon,
                                    context=context)]


def to_coupled_regions(box: Box,
                       multiregion: Multiregion,
                       *,
                       context: Context) -> Multiregion:
    return [region
            for region in multiregion
            if coupled_with_region(box, region,
                                   context=context)]
