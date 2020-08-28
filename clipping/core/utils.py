from fractions import Fraction
from itertools import (chain,
                       groupby)
from numbers import (Integral,
                     Number,
                     Rational,
                     Real)
from typing import (Any,
                    Iterable,
                    Sequence,
                    Tuple,
                    Type,
                    TypeVar)

from robust.angular import (Orientation,
                            orientation)

from clipping.hints import (Base,
                            Contour,
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


def to_mixed_base(multisegment: Multisegment,
                  multipolygon: Multipolygon) -> Base:
    return max(to_multisegment_base(multisegment),
               to_multipolygon_base(multipolygon),
               key=_bases_key)


def to_multipolygon_base(multipolygon: Multipolygon) -> Base:
    return max({to_contour_base(contour)
                for contour in to_multipolygon_contours(multipolygon)},
               key=_bases_key)


def to_multiregion_base(multipolygon: Multiregion) -> Base:
    return max({to_contour_base(region) for region in multipolygon},
               key=_bases_key)


def to_multisegment_base(multisegment: Multisegment) -> Base:
    return max(set(map(type, flatten(flatten(multisegment)))),
               key=_bases_key)


def to_contour_base(contour: Contour) -> Base:
    return max(set(map(type, flatten(contour))),
               key=_bases_key)


flatten = chain.from_iterable


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


def to_rational_multiregion(multiregion: Multiregion) -> Multiregion:
    return [to_rational_contour(region) for region in multiregion]


def to_rational_multisegment(multisegment: Multisegment) -> Multisegment:
    return [(to_rational_point(start), to_rational_point(end))
            for start, end in multisegment]


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
