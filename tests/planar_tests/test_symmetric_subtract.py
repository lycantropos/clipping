from typing import List

from hypothesis import given

from clipping.planar import (intersect,
                             subtract,
                             symmetric_subtract,
                             unite)
from tests.utils import (Multipolygon,
                         MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         rotate_sequence)
from . import strategies


@given(strategies.multipolygons_lists)
def test_basic(multipolygons: List[Multipolygon]) -> None:
    result = symmetric_subtract(*multipolygons)

    assert is_multipolygon(result)


@given(strategies.empty_multipolygons_lists)
def test_degenerate(multipolygons: List[Multipolygon]) -> None:
    assert symmetric_subtract(*multipolygons) == []


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert symmetric_subtract(multipolygon) == multipolygon
    assert symmetric_subtract(multipolygon, multipolygon) == []


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_neutral_element(empty_multipolygon_with_multipolygon
                              : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = symmetric_subtract(empty_multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_neutral_element(empty_multipolygon_with_multipolygon
                               : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = symmetric_subtract(multipolygon, empty_multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = symmetric_subtract(symmetric_subtract(left_multipolygon,
                                                   mid_multipolygon),
                                right_multipolygon)

    assert are_multipolygons_similar(
            result, symmetric_subtract(left_multipolygon,
                                       symmetric_subtract(mid_multipolygon,
                                                          right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_repeated(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = symmetric_subtract(symmetric_subtract(left_multipolygon,
                                                   mid_multipolygon),
                                symmetric_subtract(mid_multipolygon,
                                                   right_multipolygon))

    assert are_multipolygons_similar(result,
                                     symmetric_subtract(left_multipolygon,
                                                        right_multipolygon))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(left_multipolygon, right_multipolygon)

    assert result == unite(subtract(left_multipolygon, right_multipolygon),
                           subtract(right_multipolygon, left_multipolygon))
    assert result == subtract(unite(left_multipolygon, right_multipolygon),
                              intersect(right_multipolygon, left_multipolygon))


@given(strategies.non_empty_multipolygons_lists)
def test_reversals(multipolygons: List[Multipolygon]) -> None:
    first_multipolygon, *rest_multipolygons = multipolygons

    result = symmetric_subtract(first_multipolygon, *rest_multipolygons)

    assert are_multipolygons_similar(
            result,
            symmetric_subtract(reverse_multipolygon(first_multipolygon),
                               *rest_multipolygons))
    assert are_multipolygons_similar(
            result,
            symmetric_subtract(
                    reverse_multipolygon_borders(first_multipolygon),
                    *rest_multipolygons))
    assert are_multipolygons_similar(
            result,
            symmetric_subtract(reverse_multipolygon_holes(first_multipolygon),
                               *rest_multipolygons))
    assert are_multipolygons_similar(
            result,
            symmetric_subtract(
                    reverse_multipolygon_holes_contours(first_multipolygon),
                    *rest_multipolygons))


@given(strategies.multipolygons_lists)
def test_rotations(multipolygons: List[Multipolygon]) -> None:
    result = symmetric_subtract(*multipolygons)

    assert all(
            are_multipolygons_similar(result,
                                      symmetric_subtract(
                                              *rotate_sequence(multipolygons,
                                                               offset)))
            for offset in range(1, len(multipolygons)))
