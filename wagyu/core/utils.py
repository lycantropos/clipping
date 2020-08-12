import ctypes
import math
import struct
from bisect import bisect_left
from decimal import (ROUND_HALF_UP,
                     Decimal)
from fractions import Fraction
from itertools import (chain,
                       groupby)
from numbers import (Integral,
                     Number,
                     Rational,
                     Real)
from typing import (Callable,
                    Iterable,
                    List,
                    MutableSequence,
                    Sequence,
                    Type)

from wagyu.hints import (Base,
                         Contour,
                         Coordinate,
                         Multipolygon,
                         Point)
from .hints import Domain


def are_floats_greater_than_or_equal(x: float, y: float) -> bool:
    return x > y or are_floats_almost_equal(x, y)


def are_floats_greater_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x > y


def are_floats_less_than(x: float, y: float) -> bool:
    return not are_floats_almost_equal(x, y) and x < y


def is_float_almost_zero(value: float) -> bool:
    return are_floats_almost_equal(value, 0.)


def are_floats_almost_equal(left: float, right: float,
                            *,
                            max_ulps: int = 4) -> bool:
    left_bits = _double_to_bits(left)
    right_bits = _double_to_bits(right)
    return abs(left_bits - right_bits) <= max_ulps


def _double_to_bits(value: float,
                    *,
                    sign_bit_mask: int = 2 ** 63) -> int:
    result, = struct.unpack('!Q', struct.pack('!d', value))
    if sign_bit_mask & result:
        return ctypes.c_uint64(~result + 1).value
    else:
        return ctypes.c_uint64(sign_bit_mask | result).value


def rotate_sequence(sequence: Domain, index: int) -> Domain:
    return (sequence[index:] + sequence[:index]
            if 0 < index < len(sequence)
            else sequence)


flatten = chain.from_iterable


def to_multipolygon_base(multipolygon: Multipolygon) -> Base:
    return max({to_contour_base(contour)
                for contour in to_multipolygon_contours(multipolygon)},
               key=_bases_key)


def to_contour_base(contour: Contour) -> Base:
    return max(set(map(type, flatten(contour))),
               key=_bases_key)


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for border, holes in multipolygon:
        yield border
        yield from holes


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


def insort_unique(sequence: MutableSequence[Domain], value: Domain) -> None:
    index = bisect_left(sequence, value)
    if index == len(sequence) or value < sequence[index]:
        sequence.insert(index, value)


def to_unique_just_seen(sequence: Sequence[Domain]) -> List[Domain]:
    return [point for point, _ in groupby(sequence)]


def find(value: Domain, sequence: Sequence[Domain]) -> int:
    """
    Equivalent of C++'s ``std::find``.
    """
    return next((index
                 for index, element in enumerate(sequence)
                 if element is value),
                len(sequence))


def find_if(predicate: Callable[[Domain], bool],
            values: Sequence[Domain]) -> int:
    """
    Equivalent of C++'s ``std::find_if``.
    """
    for index, value in enumerate(values):
        if predicate(value):
            return index
    return len(values)


def round_towards_min(value: Coordinate) -> Coordinate:
    return (math.floor(value)
            if are_floats_almost_equal(math.floor(value) + 0.5, value)
            else round_half_up(value))


def round_towards_max(value: Coordinate) -> Coordinate:
    return (math.ceil(value)
            if are_floats_almost_equal(math.floor(value) + 0.5, value)
            else round_half_up(value))


def round_half_up(number: Coordinate) -> int:
    """
    Equivalent of C++'s ``std::llround``.
    """
    return int(Decimal(number).quantize(0, ROUND_HALF_UP))


def is_odd(number: int) -> bool:
    return bool(number % 2)


def quicksort(sequence: MutableSequence[Domain],
              comparator: Callable[[Domain, Domain], bool]):
    size = len(sequence)
    if size < 2:
        return sequence
    queue = [(0, size - 1)]
    while queue:
        index, pivot_index = low, high = queue.pop()
        element = sequence[index]
        pivot = sequence[pivot_index]
        while pivot_index > index:
            if comparator(pivot, element):
                index += 1
                element = sequence[index]
            else:
                sequence[pivot_index] = element
                pivot_index -= 1
                sequence[index] = element = sequence[pivot_index]
        sequence[pivot_index] = pivot
        low_size = pivot_index - low
        high_size = high - pivot_index
        if low_size > high_size:
            queue.append((low, pivot_index - 1))
        elif low_size > 1:
            queue.append((pivot_index + 1, high))
            queue.append((low, pivot_index - 1))
        if high_size > 1:
            queue.append((pivot_index + 1, high))
