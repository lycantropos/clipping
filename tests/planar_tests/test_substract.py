from typing import List

from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import (intersect,
                             subtract,
                             unite)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         equivalence,
                         is_multipolygon,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         rotate_sequence)
from . import strategies


@given(strategies.multipolygons_lists)
def test_basic(multipolygons: List[Multipolygon]) -> None:
    result = subtract(*multipolygons)

    assert is_multipolygon(result)


@given(strategies.empty_multipolygons_lists)
def test_degenerate(multipolygons: List[Multipolygon]) -> None:
    assert subtract(*multipolygons) == []


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert subtract(multipolygon) == multipolygon
    assert subtract(multipolygon, multipolygon) == []


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_absorbing_element(empty_multipolygon_with_multipolygon
                                : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = subtract(empty_multipolygon, multipolygon)

    assert not result


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_neutral_element(empty_multipolygon_with_multipolygon
                               : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = subtract(multipolygon, empty_multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutative_case(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract(left_multipolygon, right_multipolygon)

    assert equivalence(result == subtract(right_multipolygon,
                                          left_multipolygon),
                       are_multipolygons_similar(left_multipolygon,
                                                 right_multipolygon))


@given(strategies.multipolygons_pairs)
def test_expressing_intersection_as_difference(multipolygons_pair
                                               : MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract(left_multipolygon, subtract(left_multipolygon,
                                                  right_multipolygon))

    assert are_multipolygons_similar(result, intersect(left_multipolygon,
                                                       right_multipolygon))


@given(strategies.multipolygons_triplets)
def test_difference_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                               ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = subtract(left_multipolygon, subtract(mid_multipolygon,
                                                  right_multipolygon))

    assert are_multipolygons_similar(result,
                                     unite(subtract(left_multipolygon,
                                                    mid_multipolygon),
                                           intersect(left_multipolygon,
                                                     right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_intersection_minuend(multipolygons_triplet: MultipolygonsTriplet
                              ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = subtract(intersect(left_multipolygon, mid_multipolygon),
                      right_multipolygon)

    assert result == intersect(left_multipolygon, subtract(mid_multipolygon,
                                                           right_multipolygon))


@given(strategies.multipolygons_triplets)
def test_intersection_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = subtract(left_multipolygon, intersect(mid_multipolygon,
                                                   right_multipolygon))

    assert are_multipolygons_similar(result,
                                     unite(subtract(left_multipolygon,
                                                    mid_multipolygon),
                                           subtract(left_multipolygon,
                                                    right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_union_subtrahend(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = subtract(left_multipolygon, unite(mid_multipolygon,
                                               right_multipolygon))

    assert are_multipolygons_similar(result,
                                     intersect(subtract(left_multipolygon,
                                                        mid_multipolygon),
                                               subtract(left_multipolygon,
                                                        right_multipolygon)))


@given(strategies.non_empty_multipolygons_lists)
def test_reversals(multipolygons: List[Multipolygon]) -> None:
    first_multipolygon, *rest_multipolygons = multipolygons

    result = subtract(first_multipolygon, *rest_multipolygons)

    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon(first_multipolygon),
                             *rest_multipolygons))
    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon_borders(first_multipolygon),
                             *rest_multipolygons))
    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon_holes(first_multipolygon),
                             *rest_multipolygons))
    assert are_multipolygons_similar(
            result,
            subtract(reverse_multipolygon_holes_contours(first_multipolygon),
                     *rest_multipolygons))


@given(strategies.non_empty_multipolygons_lists)
def test_rotations(multipolygons: List[Multipolygon]) -> None:
    first_multipolygon, *rest_multipolygons = multipolygons

    result = subtract(first_multipolygon, *rest_multipolygons)

    assert all(
            are_multipolygons_similar(
                    result,
                    subtract(first_multipolygon,
                             *rotate_sequence(rest_multipolygons, offset)))
            for offset in range(1, len(rest_multipolygons)))
