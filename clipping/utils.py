from fractions import Fraction
from itertools import chain
from numbers import (Integral,
                     Number,
                     Rational,
                     Real)
from typing import (Iterable,
                    List,
                    Sequence,
                    Type)

from bentley_ottmann.angular import (Orientation,
                                     to_orientation)

from .hints import (Base,
                    BoundingBox,
                    Contour,
                    Multipolygon,
                    Point,
                    Polygon,
                    Segment)


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for border, holes in multipolygon:
        yield border
        yield from holes


def to_bounding_box(multipolygon: Multipolygon) -> BoundingBox:
    ((first_vertex, *rest_vertices), _), *rest_polygons = multipolygon
    x_min, y_min = x_max, y_max = first_vertex
    for x, y in _flatten([rest_vertices]
                         + [border for border, _ in rest_polygons]):
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def to_segments(contour: Contour) -> List[Segment]:
    return [(contour[index], contour[(index + 1) % len(contour)])
            for index in range(len(contour))]


def to_multipolygon_base(multipolygon: Multipolygon) -> Base:
    return max({to_contour_base(contour)
                for contour in to_multipolygon_contours(multipolygon)},
               key=_bases_key)


def to_contour_base(contour: Contour) -> Base:
    return max(set(map(type, _flatten(contour))),
               key=_bases_key)


_flatten = chain.from_iterable


def _bases_key(base: Base,
               types: Sequence[Type[Number]] = (Integral, Rational, Real)
               ) -> int:
    try:
        return next(index
                    for index, type_ in enumerate(types)
                    if issubclass(base, type_))
    except StopIteration:
        if issubclass(base, Number):
            raise TypeError('{type} numbers are not supported.'
                            .format(type=base))
        else:
            raise TypeError('{type} is not recognized as a number type.'
                            .format(type=base))


def to_rational_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    return [(to_rational_contour(border), [to_rational_contour(hole)
                                           for hole in holes])
            for border, holes in multipolygon]


def to_rational_contour(contour: Contour) -> Contour:
    return [to_rational_point(vertex) for vertex in contour]


def to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_rational_point(start), to_rational_point(end)


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)


def shrink_collinear_vertices(contour: Contour) -> None:
    self_intersections, visited = set(), set()
    visit = visited.add
    for vertex in contour:
        if vertex in visited:
            self_intersections.add(vertex)
        else:
            visit(vertex)
    for index in range(len(contour)):
        while (max(index, 2) < len(contour)
               and contour[index - 1] not in self_intersections
               and (to_orientation(contour[index - 2], contour[index - 1],
                                   contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index - 1]


def to_first_boundary_vertex(polygon: Polygon) -> Point:
    boundary, _ = polygon
    return boundary[0]
