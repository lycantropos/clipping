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

from clipping.hints import (Base,
                            Contour,
                            Coordinate,
                            Multipolygon,
                            Multisegment,
                            Point,
                            Polygon,
                            Segment)


def all_equal(iterable: Iterable[Any]) -> bool:
    groups = groupby(iterable)
    return next(groups, True) and not next(groups, False)


Domain = TypeVar('Domain')


def sort_pair(pair: Tuple[Domain, Domain]) -> Tuple[Domain, Domain]:
    first, second = pair
    return (first, second) if first < second else (second, first)


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for border, holes in multipolygon:
        yield border
        yield from holes


def contour_to_segments(contour: Contour) -> Iterable[Segment]:
    return ((contour[index - 1], contour[index])
            for index in range(len(contour)))


def to_mixed_base(multisegment: Multisegment,
                  multipolygon: Multipolygon) -> Base:
    return max(to_multisegment_base(multisegment),
               to_multipolygon_base(multipolygon),
               key=_bases_key)


def to_multipolygon_base(multipolygon: Multipolygon) -> Base:
    return max({to_contour_base(contour)
                for contour in to_multipolygon_contours(multipolygon)},
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


def to_multisegment_x_max(multisegment: Multisegment) -> Coordinate:
    return max(x for x, _ in flatten(multisegment))
