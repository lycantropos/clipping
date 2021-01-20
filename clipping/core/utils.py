from itertools import (chain,
                       groupby)
from typing import (Any,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.base import (Context,
                         Orientation)
from ground.hints import (Contour,
                          Coordinate,
                          Point,
                          Polygon,
                          Segment)

from .hints import (Multiregion,
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


def polygon_to_oriented_edges_endpoints(polygon: Polygon,
                                        *,
                                        context: Context
                                        ) -> Iterable[SegmentEndpoints]:
    yield from contour_to_oriented_edges_endpoints(polygon.border,
                                                   clockwise=False,
                                                   context=context)
    for hole in polygon.holes:
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
    return context.angle_orientation(vertices[index - 1], vertices[index],
                                     vertices[(index + 1) % len(vertices)])


flatten = chain.from_iterable


def to_first_border_vertex(polygon: Polygon) -> Point:
    return polygon.border.vertices[0]


def to_multiregion_x_max(multiregion: Multiregion) -> Coordinate:
    return max(vertex.x
               for border in multiregion
               for vertex in border.vertices)


def to_polygons_x_max(polygons: Sequence[Polygon]) -> Coordinate:
    return max(vertex.x
               for polygon in polygons
               for vertex in polygon.border.vertices)


def to_segments_x_max(segments: Sequence[Segment]) -> Coordinate:
    return max(max(segment.start.x, segment.end.x) for segment in segments)


def shrink_collinear_vertices(vertices: List[Point],
                              *,
                              context: Context) -> None:
    index = -len(vertices) + 1
    orienteer = context.angle_orientation
    while index < 0:
        while (max(2, -index) < len(vertices)
               and orienteer(vertices[index + 1], vertices[index + 2],
                             vertices[index]) is Orientation.COLLINEAR):
            del vertices[index + 1]
        index += 1
    while index < len(vertices):
        while (max(2, index) < len(vertices)
               and orienteer(vertices[index - 1], vertices[index - 2],
                             vertices[index]) is Orientation.COLLINEAR):
            del vertices[index - 1]
        index += 1


def segments_to_endpoints(segments: Sequence[Segment]
                          ) -> Iterable[SegmentEndpoints]:
    return ((segment.start, segment.end) for segment in segments)


def endpoints_to_segments(endpoints: Iterable[SegmentEndpoints],
                          *,
                          context: Context) -> Sequence[Segment]:
    segment_cls = context.segment_cls
    return [segment_cls(start, end) for start, end in endpoints]
