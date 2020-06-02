from fractions import Fraction
from itertools import (chain,
                       groupby)
from numbers import (Integral,
                     Number,
                     Rational,
                     Real)
from typing import (Any,
                    Iterable,
                    List,
                    Sequence,
                    Type)

from clipping.hints import (Base,
                            BoundingBox,
                            Contour,
                            Coordinate,
                            Multipolygon,
                            Point,
                            Polygon,
                            Segment)


def all_equal(iterable: Iterable[Any]) -> bool:
    groups = groupby(iterable)
    return next(groups, True) and not next(groups, False)


def to_polygons_contours(polygons: Iterable[Polygon]) -> Iterable[Contour]:
    for border, holes in polygons:
        yield border
        yield from holes


def multipolygon_to_bounding_box(multipolygon: Multipolygon) -> BoundingBox:
    vertices = flatten(border for border, _ in multipolygon)
    x_min, y_min = x_max, y_max = next(vertices)
    for x, y in vertices:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def are_bounding_boxes_disjoint(left: BoundingBox, right: BoundingBox) -> bool:
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min)


def to_segments(contour: Contour) -> List[Segment]:
    return [(contour[index], contour[(index + 1) % len(contour)])
            for index in range(len(contour))]


def to_polygons_base(polygons: Iterable[Polygon]) -> Base:
    return max({to_contour_base(contour)
                for contour in to_polygons_contours(polygons)},
               key=_bases_key)


def to_contour_base(contour: Contour) -> Base:
    return max(set(map(type, flatten(contour))),
               key=_bases_key)


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


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)


def to_first_boundary_vertex(polygon: Polygon) -> Point:
    boundary, _ = polygon
    return boundary[0]


def to_multipolygon_x_max(multipolygon: Multipolygon) -> Coordinate:
    return max(x for border, _ in multipolygon for x, _ in border)


flatten = chain.from_iterable
