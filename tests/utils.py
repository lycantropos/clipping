from numbers import (Number,
                     Real)
from operator import itemgetter
from typing import (Any,
                    Callable,
                    Iterable,
                    Optional,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from robust.angular import (Orientation,
                            orientation)

from clipping.core.utils import (to_contour_base,
                                 to_first_boundary_vertex)
from clipping.hints import (Contour,
                            Multipolygon)

Strategy = SearchStrategy
Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
MultipolygonsPair = Tuple[Multipolygon, Multipolygon]
MultipolygonsTriplet = Tuple[Multipolygon, Multipolygon, Multipolygon]


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


_sentinel = object()


def to_index_min(values: Iterable[Domain],
                 *,
                 key: Optional[Key] = None,
                 default: Any = _sentinel) -> int:
    kwargs = {}
    if key is not None:
        kwargs['key'] = lambda value_with_index: key(value_with_index[0])
    if default is not _sentinel:
        kwargs['default'] = default
    return min(((value, index)
                for index, value in enumerate(values)),
               **kwargs)[1]


def are_multipolygons_similar(left: Multipolygon, right: Multipolygon) -> bool:
    return normalize_multipolygon(left) == normalize_multipolygon(right)


def normalize_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    result = [(normalize_contour(boundary), sorted([normalize_contour(hole)
                                                    for hole in holes],
                                                   key=itemgetter(0)))
              for boundary, holes in multipolygon]
    result.sort(key=to_first_boundary_vertex)
    return result


def normalize_contour(contour: Contour) -> Contour:
    return to_counterclockwise_contour(rotate_sequence(contour,
                                                       to_index_min(contour)))


def to_counterclockwise_contour(contour: Contour) -> Contour:
    if _to_first_angle_orientation(contour) is not Orientation.CLOCKWISE:
        contour = contour[:1] + contour[1:][::-1]
    return contour


def _to_first_angle_orientation(contour: Contour) -> Orientation:
    first_angle_vertices = [contour[-1], contour[0], contour[1]]
    if not issubclass(to_contour_base(first_angle_vertices), Real):
        first_angle_vertices = [(float(x), float(y))
                                for x, y in first_angle_vertices]
    return orientation(*first_angle_vertices)


def rotate_sequence(sequence: Domain, index: int) -> Domain:
    return sequence[index:] + sequence[:index]


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_triplets(strategy: Strategy[Domain]
                ) -> Strategy[Tuple[Domain, Domain, Domain]]:
    return strategies.tuples(strategy, strategy, strategy)


def is_geometry_collection(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 3
            and all(isinstance(element, list)
                    for element in object_)
            and all(map(is_point, object_[0]))
            and all(map(is_segment, object_[1]))
            and all(map(is_polygon, object_[2])))


def is_multipolygon(object_: Any) -> bool:
    return (isinstance(object_, list)
            and all(map(is_polygon, object_)))


def is_polygon(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 2
            and is_contour(object_[0])
            and isinstance(object_[1], list)
            and all(map(is_contour, object_[1])))


def is_contour(object_: Any) -> bool:
    return (isinstance(object_, list)
            and len(object_) >= 3
            and all(map(is_point, object_)))


def is_segment(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 2
            and all(map(is_point, object_))
            and len(set(object_)) == 2)


def is_point(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 2
            and all(isinstance(coordinate, Number)
                    for coordinate in object_)
            and len(set(map(type, object_))) == 1)


def reverse_polygons(multipolygon: Multipolygon) -> Multipolygon:
    return [(border[::-1], [hole[::-1] for hole in holes])
            for border, holes in multipolygon]
