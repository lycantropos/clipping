from typing import (Iterable,
                    Sequence)

from ground.base import Context
from ground.hints import (Box,
                          Contour,
                          Point,
                          Polygon,
                          Segment)
from orient.planar import (Relation,
                           point_in_region,
                           segment_in_contour,
                           segment_in_region)

from .hints import (Multiregion,
                    Region,
                    SegmentEndpoints)
from .utils import (contour_to_edges_endpoints,
                    flatten)


def from_contour(contour: Contour,
                 *,
                 context: Context) -> Box:
    """
    Builds box from contour.
    """
    return from_points(contour.vertices,
                       context=context)


def from_segments(segments: Sequence[Segment],
                  *,
                  context: Context) -> Box:
    """
    Builds box from multisegment.
    """
    return from_points(flatten((segment.start, segment.end)
                               for segment in segments),
                       context=context)


def from_polygons(polygons: Sequence[Polygon],
                  *,
                  context: Context) -> Box:
    """
    Builds box from multipolygon.
    """
    return from_points(flatten(polygon.border.vertices
                               for polygon in polygons),
                       context=context)


def from_multiregion(multiregion: Multiregion,
                     *,
                     context: Context) -> Box:
    """
    Builds box from multiregion.
    """
    return from_points(flatten(region.vertices for region in multiregion),
                       context=context)


def from_points(points: Iterable[Point],
                *,
                context: Context) -> Box:
    """
    Builds box from points.
    """
    points = iter(points)
    point = next(points)
    min_x, min_y = max_x, max_y = point.x, point.y
    for point in points:
        x, y = point.x, point.y
        if x < min_x:
            min_x = x
        elif x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        elif y > max_y:
            max_y = y
    return context.box_cls(min_x, max_x, min_y, max_y)


def from_segment(segment: Segment,
                 *,
                 context: Context) -> Box:
    """
    Builds box from segment.
    """
    return from_points((segment.start, segment.end),
                       context=context)


def disjoint_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes do not intersect.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> disjoint_with(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    False
    >>> disjoint_with(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    False
    >>> disjoint_with(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    False
    >>> disjoint_with(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    False
    >>> disjoint_with(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    True
    """
    return (right.max_x < left.min_x or left.max_x < right.min_x
            or right.max_y < left.min_y or left.max_y < right.min_y)


def intersects_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> intersects_with(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    True
    >>> intersects_with(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    True
    >>> intersects_with(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    True
    >>> intersects_with(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    True
    >>> intersects_with(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return (right.min_x <= left.max_x and left.min_x <= right.max_x
            and right.min_y <= left.max_y and left.min_y <= right.max_y)


def coupled_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect in some region or by the edge.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> coupled_with(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    True
    >>> coupled_with(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    True
    >>> coupled_with(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    True
    >>> coupled_with(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    False
    >>> coupled_with(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return (intersects_with(left, right)
            and (not touches_with(left, right)
                 or edges_overlap_with(left, right)))


def touches_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect at point or by the edge.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> touches_with(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    False
    >>> touches_with(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    False
    >>> touches_with(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    True
    >>> touches_with(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    True
    >>> touches_with(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return ((left.min_x == right.max_x or left.max_x == right.min_x)
            and (left.min_y <= right.max_y and right.min_y <= left.max_y)
            or (left.min_x <= right.max_x and right.min_x <= left.max_x)
            and (left.min_y == right.max_y or right.min_y == left.max_y))


def edges_overlap_with(left: Box, right: Box) -> bool:
    """
    Checks if boxes intersect by the edge.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> edges_overlap_with(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    False
    >>> edges_overlap_with(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    False
    >>> edges_overlap_with(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    True
    >>> edges_overlap_with(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    False
    >>> edges_overlap_with(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return ((left.min_x == right.max_x or left.max_x == right.min_x)
            and (left.min_y < right.max_y and right.min_y < left.max_y)
            or (left.min_x < right.max_x and right.min_x < left.max_x)
            and (left.min_y == right.max_y or right.min_y == left.max_y))


def is_subset_of(test: Box, goal: Box) -> bool:
    """
    Checks if the box is the subset of the other.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> is_subset_of(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    True
    >>> is_subset_of(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    False
    >>> is_subset_of(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    False
    >>> is_subset_of(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    False
    >>> is_subset_of(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return (goal.min_x <= test.min_x and test.max_x <= goal.max_x
            and goal.min_y <= test.min_y and test.max_y <= goal.max_y)


def within_of(test: Box, goal: Box) -> bool:
    """
    Checks if the box is contained in an interior of the other.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Box = context.box_cls
    >>> within_of(Box(0, 2, 0, 2), Box(0, 2, 0, 2))
    False
    >>> within_of(Box(0, 2, 0, 2), Box(1, 3, 1, 3))
    False
    >>> within_of(Box(0, 2, 0, 2), Box(2, 4, 0, 2))
    False
    >>> within_of(Box(0, 2, 0, 2), Box(2, 4, 2, 4))
    False
    >>> within_of(Box(0, 2, 0, 2), Box(2, 4, 3, 5))
    False
    """
    return (goal.min_x < test.min_x and test.max_x < goal.max_x
            and goal.min_y < test.min_y and test.max_y < goal.max_y)


def intersects_with_segment(box: Box,
                            start: Point,
                            end: Point,
                            *,
                            context: Context) -> bool:
    """
    Checks if the box intersects the segment.
    """
    segment_box = from_points((start, end),
                              context=context)
    return (intersects_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(context.segments_relation(edge_start, edge_end, start,
                                                  end) is not Relation.DISJOINT
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
    segment_box = from_segment(segment,
                               context=context)
    return (coupled_with(segment_box, box)
            and (is_subset_of(segment_box, box)
                 or any(context.segments_relation(edge_start, edge_end,
                                                  segment.start, segment.end)
                        not in (Relation.TOUCH, Relation.DISJOINT)
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
            and all(context.segments_relation(edge_start, edge_end,
                                              border_edge_start,
                                              border_edge_end)
                    is Relation.DISJOINT
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
    return any(is_subset_of(box, from_contour(region,
                                              context=context))
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
    border = polygon.border
    polygon_box = from_contour(border,
                               context=context)
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
            and all(context.segments_relation(edge_start, edge_end,
                                              border_edge_start,
                                              border_edge_end)
                    is Relation.DISJOINT
                    for edge_start, edge_end
                    in to_edges_endpoints(box,
                                          context=context)
                    for border_edge_start, border_edge_end
                    in contour_to_edges_endpoints(border))):
        return not any(within_of(box, from_contour(hole,
                                                   context=context))
                       and within_of_region(box, hole,
                                            context=context)
                       for hole in polygon.holes)
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
    region_box = from_contour(region,
                              context=context)
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
    border = polygon.border
    polygon_box = from_contour(border,
                               context=context)
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
                or not is_subset_of_multiregion(box, polygon.holes,
                                                context=context))
    else:
        return (not is_subset_of_multiregion(box, polygon.holes,
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
    region_box = from_contour(region,
                              context=context)
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
    return (box.min_x <= point.x <= box.max_x
            and box.min_y <= point.y <= box.max_y)


def covers_point(box: Box, point: Point) -> bool:
    return box.min_x < point.x < box.max_x and box.min_y < point.y < box.max_y


def to_vertices(box: Box,
                *,
                context: Context) -> Sequence[Point]:
    point_cls = context.point_cls
    return (point_cls(box.min_x, box.min_y), point_cls(box.max_x, box.min_y),
            point_cls(box.max_x, box.max_y), point_cls(box.min_x, box.max_y))


def to_edges_endpoints(box: Box,
                       *,
                       context: Context) -> Sequence[SegmentEndpoints]:
    point_cls = context.point_cls
    return ((point_cls(box.min_x, box.min_y), point_cls(box.max_x, box.min_y)),
            (point_cls(box.max_x, box.min_y), point_cls(box.max_x, box.max_y)),
            (point_cls(box.min_x, box.max_y), point_cls(box.max_x, box.max_y)),
            (point_cls(box.min_x, box.min_y), point_cls(box.min_x, box.max_y)))


def to_edges(box: Box,
             *,
             context: Context) -> Sequence[Segment]:
    point_cls, segment_cls = context.point_cls, context.segment_cls
    return (segment_cls(point_cls(box.min_x, box.min_y),
                        point_cls(box.max_x, box.min_y)),
            segment_cls(point_cls(box.max_x, box.min_y),
                        point_cls(box.max_x, box.max_y)),
            segment_cls(point_cls(box.min_x, box.max_y),
                        point_cls(box.max_x, box.max_y)),
            segment_cls(point_cls(box.min_x, box.min_y),
                        point_cls(box.min_x, box.max_y)))


def to_intersecting_segments(box: Box,
                             segments: Sequence[Segment],
                             *,
                             context: Context) -> Sequence[Segment]:
    return [segment
            for segment in segments
            if intersects_with_segment(box, segment.start, segment.end,
                                       context=context)]


def to_coupled_segments(box: Box,
                        segments: Sequence[Segment],
                        *,
                        context: Context) -> Sequence[Segment]:
    return [segment
            for segment in segments
            if coupled_with_segment(box, segment,
                                    context=context)]


def to_intersecting_polygons(box: Box,
                             polygons: Sequence[Polygon],
                             *,
                             context: Context) -> Sequence[Polygon]:
    return [polygon
            for polygon in polygons
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
                        polygons: Sequence[Polygon],
                        *,
                        context: Context) -> Sequence[Polygon]:
    return [polygon
            for polygon in polygons
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
