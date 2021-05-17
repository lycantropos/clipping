import sys
from itertools import (chain,
                       groupby)
from typing import (AbstractSet,
                    Any,
                    Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.base import (Context,
                         Orientation)
from ground.hints import (Contour,
                          Point,
                          Polygon,
                          Scalar,
                          Segment)

from .hints import (Region,
                    SegmentEndpoints)


def all_equal(iterable: Iterable[Any]) -> bool:
    groups = groupby(iterable)
    return next(groups, True) and not next(groups, False)


_T = TypeVar('_T')


def pairwise(iterable: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    iterator = iter(iterable)
    element = next(iterator, None)
    for next_element in iterator:
        yield element, next_element
        element = next_element


def polygon_to_oriented_edges_endpoints(polygon: Polygon,
                                        context: Context
                                        ) -> Iterable[SegmentEndpoints]:
    yield from contour_to_oriented_edges_endpoints(polygon.border, context)
    for hole in polygon.holes:
        yield from contour_to_oriented_edges_endpoints(hole, context, True)


def contour_to_oriented_edges_endpoints(contour: Contour,
                                        context: Context,
                                        clockwise: bool = False
                                        ) -> Iterable[SegmentEndpoints]:
    vertices = contour.vertices
    return (((vertices[index - 1], vertices[index])
             for index in range(len(vertices)))
            if (to_contour_orientation(contour, context)
                is (Orientation.CLOCKWISE
                    if clockwise
                    else Orientation.COUNTERCLOCKWISE))
            else ((vertices[index], vertices[index - 1])
                  for index in range(len(vertices) - 1, -1, -1)))


def to_contour_orientation(contour: Contour, context: Context) -> Orientation:
    vertices = contour.vertices
    index = min(range(len(vertices)),
                key=vertices.__getitem__)
    return context.angle_orientation(vertices[index - 1], vertices[index],
                                     vertices[(index + 1) % len(vertices)])


flatten = chain.from_iterable


def to_first_border_vertex(polygon: Polygon) -> Point:
    return polygon.border.vertices[0]


def to_regions_x_max(regions: Sequence[Region]) -> Scalar:
    return max(vertex.x
               for border in regions
               for vertex in border.vertices)


def to_polygons_x_max(polygons: Sequence[Polygon]) -> Scalar:
    return max(vertex.x
               for polygon in polygons
               for vertex in polygon.border.vertices)


def to_segments_x_max(segments: Sequence[Segment]) -> Scalar:
    return max(max(segment.start.x, segment.end.x) for segment in segments)


def shrink_collinear_vertices(vertices: List[Point], context: Context) -> None:
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
                          context: Context) -> List[Segment]:
    segment_cls = context.segment_cls
    return [segment_cls(start, end) for start, end in endpoints]


def to_endpoints(segment: Segment) -> SegmentEndpoints:
    return segment.start, segment.end


if sys.version_info < (3, 6):
    from collections import OrderedDict
else:
    OrderedDict = dict


def to_ordered_set(values: Iterable[_T]) -> AbstractSet[_T]:
    return OrderedDict.fromkeys(values).keys()
