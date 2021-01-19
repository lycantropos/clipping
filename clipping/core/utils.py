from itertools import (chain,
                       groupby)
from typing import (Any,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.base import (Context,
                         Orientation,
                         Relation,
                         get_context)
from ground.hints import (Contour,
                          Point,
                          Segment)

from .hints import (Coordinate,
                    Multipolygon,
                    Multiregion,
                    Multisegment,
                    Polygon,
                    SegmentEndpoints)


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


def polygon_to_oriented_edges_endpoints(polygon: Polygon,
                                        *,
                                        context: Context
                                        ) -> Iterable[SegmentEndpoints]:
    border, holes = polygon
    yield from contour_to_oriented_edges_endpoints(border,
                                                   clockwise=False,
                                                   context=context)
    for hole in holes:
        yield from contour_to_oriented_edges_endpoints(hole,
                                                       clockwise=True,
                                                       context=context)


def contour_to_oriented_edges_endpoints(contour: Contour,
                                        *,
                                        clockwise: bool = False,
                                        context: Context
                                        ) -> Iterable[SegmentEndpoints]:
    vertices = contour.vertices
    return (((vertices[index - 1], vertices[index])
             for index in range(len(vertices)))
            if (to_contour_orientation(contour,
                                       context=context)
                is (Orientation.CLOCKWISE
                    if clockwise
                    else Orientation.COUNTERCLOCKWISE))
            else ((vertices[index], vertices[index - 1])
                  for index in range(len(vertices) - 1, -1, -1)))


def contour_to_edges_endpoints(contour: Contour) -> Iterable[SegmentEndpoints]:
    vertices = contour.vertices
    return ((vertices[index - 1], vertices[index])
            for index in range(len(vertices)))


def to_contour_orientation(contour: Contour,
                           *,
                           context: Context) -> Orientation:
    vertices = contour.vertices
    index = min(range(len(vertices)),
                key=vertices.__getitem__)
    return orientation(context, vertices[index], vertices[index - 1],
                       vertices[(index + 1) % len(vertices)])


flatten = chain.from_iterable


def to_first_border_vertex(polygon: Polygon) -> Point:
    border, _ = polygon
    return border.vertices[0]


def to_multipolygon_x_max(multipolygon: Multipolygon) -> Coordinate:
    return max(vertex.x
               for border, _ in multipolygon
               for vertex in border.vertices)


def to_multiregion_x_max(multiregion: Multiregion) -> Coordinate:
    return max(vertex.x
               for border in multiregion
               for vertex in border.vertices)


def to_multisegment_x_max(multisegment: Multisegment) -> Coordinate:
    return max(max(segment.start.x, segment.end.x) for segment in multisegment)


def shrink_collinear_vertices(vertices: List[Point],
                              *,
                              context: Context) -> None:
    index = -len(vertices) + 1
    while index < 0:
        while (max(2, -index) < len(vertices)
               and (orientation(context, vertices[index + 2],
                                vertices[index + 1], vertices[index])
                    is Orientation.COLLINEAR)):
            del vertices[index + 1]
        index += 1
    while index < len(vertices):
        while (max(2, index) < len(vertices)
               and (orientation(context, vertices[index - 2],
                                vertices[index - 1], vertices[index])
                    is Orientation.COLLINEAR)):
            del vertices[index - 1]
        index += 1


Orientation = Orientation


def orientation(context, first, vertex, second):
    return context.angle_orientation(vertex, first, second)


SegmentsRelation = Relation


def segments_intersection(context: Context, first_start, first_end,
                          second_start, second_end):
    return context.segments_intersection(first_start, first_end, second_start,
                                         second_end)


def segments_relation(first_start, first_end, second_start, second_end):
    context = get_context()
    return context.segments_relation(first_start, first_end, second_start,
                                     second_end)


def multisegment_to_endpoints(multisegment: Multisegment
                              ) -> Iterable[SegmentEndpoints]:
    return segments_to_endpoints(multisegment)


def segments_to_endpoints(segments: Sequence[Segment]
                          ) -> Iterable[SegmentEndpoints]:
    return ((segment.start, segment.end) for segment in segments)


def endpoints_to_multisegment(endpoints: Iterable[SegmentEndpoints],
                              *,
                              context: Context) -> Multisegment:
    segment_cls = context.segment_cls
    return [segment_cls(start, end) for start, end in endpoints]
