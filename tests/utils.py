from numbers import (Number,
                     Real)
from operator import itemgetter
from typing import (Any,
                    Callable,
                    Sequence,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from orient.planar import (Relation,
                           multisegment_in_multisegment)
from robust.angular import (Orientation,
                            orientation)

from clipping.core.hints import BoundingBox
from clipping.core.utils import (to_contour_base,
                                 to_first_boundary_vertex)
from clipping.hints import (Contour,
                            Mix,
                            Multipoint,
                            Multipolygon,
                            Multisegment,
                            Segment)

Strategy = SearchStrategy
Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
BoundingBoxesPair = Tuple[BoundingBox, BoundingBox]
BoundingBoxesTriplet = Tuple[BoundingBox, BoundingBox, BoundingBox]
MultisegmentsPair = Tuple[Multisegment, Multisegment]
MultisegmentsTriplet = Tuple[Multisegment, Multisegment, Multisegment]
MultipolygonWithMultisegment = Tuple[Multipolygon, Multisegment]
MultipolygonsPair = Tuple[Multipolygon, Multipolygon]
MultipolygonsTriplet = Tuple[Multipolygon, Multipolygon, Multipolygon]


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def arg_min(values: Sequence[Domain]) -> int:
    return min(range(len(values)),
               key=values.__getitem__)


def mix_equivalent_to_multisegment(mix: Mix, other: Multisegment) -> bool:
    multipoint, multisegment, multipolygon = mix
    return (not multipoint and not multipolygon
            and are_multisegments_equivalent(multisegment, other))


def mix_similar_to_multipolygon(mix: Mix, other: Multipolygon) -> bool:
    multipoint, multisegment, multipolygon = mix
    return (not multipoint and not multisegment
            and are_multipolygons_similar(multipolygon, other))


def are_mixes_similar(left: Mix, right: Mix) -> bool:
    left_multipoint, left_multisegment, left_multipolygon = left
    right_multipoint, right_multisegment, right_multipolygon = right
    return (are_multipoints_similar(left_multipoint, right_multipoint)
            and are_multisegments_similar(left_multisegment,
                                          right_multisegment)
            and are_multipolygons_similar(left_multipolygon,
                                          right_multipolygon))


def are_multipoints_similar(left: Multipoint, right: Multipoint) -> bool:
    return len(left) == len(right) and frozenset(left) == frozenset(right)


def are_multisegments_similar(left: Multisegment, right: Multisegment) -> bool:
    return (len(left) == len(right)
            and (frozenset(map(frozenset, left))
                 == frozenset(map(frozenset, right))))


def are_multisegments_equivalent(left: Multisegment,
                                 right: Multisegment) -> bool:
    return (not (left or right)
            or sorted(map(sort_pair, left)) == sorted(map(sort_pair, right))
            or multisegment_in_multisegment(left, right) is Relation.EQUAL)


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
                                                       arg_min(contour)))


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


def is_mix(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 3
            and is_multipoint(object_[0])
            and is_multisegment(object_[1])
            and is_multipolygon(object_[2]))


def is_multipoint(object_: Any) -> bool:
    return isinstance(object_, list) and all(map(is_point, object_))


def is_multisegment(object_: Any) -> bool:
    return isinstance(object_, list) and all(map(is_segment, object_))


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


def reverse_multipolygon_borders(multipolygon: Multipolygon) -> Multipolygon:
    return [(border[::-1], holes) for border, holes in multipolygon]


def reverse_multipolygon_holes(multipolygon: Multipolygon) -> Multipolygon:
    return [(border, holes[::-1]) for border, holes in multipolygon]


def reverse_multipolygon_holes_contours(multipolygon: Multipolygon
                                        ) -> Multipolygon:
    return [(border, [hole[::-1] for hole in holes])
            for border, holes in multipolygon]


def reverse_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    return multipolygon[::-1]


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return multisegment[::-1]


def reverse_multisegment_endpoints(multisegment: Multisegment) -> Multisegment:
    return [reverse_segment(segment) for segment in multisegment]


def reverse_segment(segment: Segment) -> Segment:
    return segment[::-1]


def sort_pair(pair: Tuple[Domain, Domain]) -> Tuple[Domain, Domain]:
    first, second = pair
    return pair if first < second else (second, first)
