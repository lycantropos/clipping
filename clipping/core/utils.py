from itertools import (chain,
                       groupby)
from typing import (Any,
                    Iterable,
                    Tuple,
                    TypeVar)

from ground.base import Orientation, Relation, get_context

from clipping.hints import (Contour,
                            Coordinate,
                            Multipolygon,
                            Multiregion,
                            Multisegment,
                            Point,
                            Polygon,
                            Segment)


def all_equal(iterable: Iterable[Any]) -> bool:
    groups = groupby(iterable)
    return next(groups, True) and not next(groups, False)


Domain = TypeVar('Domain')


def pairwise(iterable: Iterable[Domain]) -> Iterable[Tuple[Domain, Domain]]:
    iterator = iter(iterable)
    element = next(iterator, None)
    for next_element in iterator:
        yield element, next_element
        element = next_element


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for border, holes in multipolygon:
        yield border
        yield from holes


def polygon_to_oriented_segments(polygon: Polygon) -> Iterable[Segment]:
    border, holes = polygon
    yield from contour_to_oriented_segments(border,
                                            clockwise=False)
    for hole in holes:
        yield from contour_to_oriented_segments(hole,
                                                clockwise=True)


def contour_to_oriented_segments(contour: Contour,
                                 *,
                                 clockwise: bool = False) -> Iterable[Segment]:
    return (((contour[index - 1], contour[index])
             for index in range(len(contour)))
            if (to_contour_orientation(contour)
                is (Orientation.CLOCKWISE
                    if clockwise
                    else Orientation.COUNTERCLOCKWISE))
            else ((contour[index], contour[index - 1])
                  for index in range(len(contour) - 1, -1, -1)))


def contour_to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))


def to_contour_orientation(contour: Contour) -> Orientation:
    index = min(range(len(contour)),
                key=contour.__getitem__)
    return orientation(contour[index], contour[index - 1],
                       contour[(index + 1) % len(contour)])


flatten = chain.from_iterable


def to_first_boundary_vertex(polygon: Polygon) -> Point:
    boundary, _ = polygon
    return boundary[0]


def to_multipolygon_x_max(multipolygon: Multipolygon) -> Coordinate:
    return max(x for border, _ in multipolygon for x, _ in border)


def to_multiregion_x_max(multiregion: Multiregion) -> Coordinate:
    return max(x for border in multiregion for x, _ in border)


def to_multisegment_x_max(multisegment: Multisegment) -> Coordinate:
    return max(x for x, _ in flatten(multisegment))


def shrink_collinear_vertices(contour: Contour) -> None:
    index = -len(contour) + 1
    while index < 0:
        while (max(2, -index) < len(contour)
               and (orientation(contour[index + 2], contour[index + 1],
                                contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index + 1]
        index += 1
    while index < len(contour):
        while (max(2, index) < len(contour)
               and (orientation(contour[index - 2], contour[index - 1],
                                contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index - 1]
        index += 1


Orientation = Orientation


def orientation(first, vertex, second):
    context = get_context()
    point_cls = context.point_cls
    return context.angle_orientation(point_cls(*vertex), point_cls(*first),
                                     point_cls(*second))


SegmentsRelation = Relation


def segments_intersection(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    point_cls = context.point_cls
    result = context.segments_intersection(point_cls(*first_start),
                                           point_cls(*first_end),
                                           point_cls(*second_start),
                                           point_cls(*second_end))
    return result.x, result.y


def segments_relation(first, second):
    first_start, first_end = first
    second_start, second_end = second
    context = get_context()
    point_cls = context.point_cls
    return context.segments_relation(point_cls(*first_start),
                                     point_cls(*first_end),
                                     point_cls(*second_start),
                                     point_cls(*second_end))
