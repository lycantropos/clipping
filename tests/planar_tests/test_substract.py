from hypothesis import given

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
                         reverse_multipolygon_holes_contours)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract(left_multipolygon, right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_absorbing_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = subtract(empty_multipolygon, multipolygon)

    assert not result


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_neutral_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
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
def test_expressing_intersection_as_difference(
        multipolygons_pair: MultipolygonsPair) -> None:
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
def test_intersection_subtrahend(
        multipolygons_triplet: MultipolygonsTriplet) -> None:
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


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract(left_multipolygon, right_multipolygon)

    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon(left_multipolygon),
                             right_multipolygon))
    assert result == subtract(
            left_multipolygon, reverse_multipolygon(right_multipolygon))
    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon_borders(left_multipolygon),
                             right_multipolygon))
    assert result == subtract(
            left_multipolygon,
            reverse_multipolygon_borders(right_multipolygon))
    assert are_multipolygons_similar(
            result, subtract(reverse_multipolygon_holes(left_multipolygon),
                             right_multipolygon))
    assert result == subtract(left_multipolygon,
                              reverse_multipolygon_holes(right_multipolygon))
    assert are_multipolygons_similar(
            result,
            subtract(reverse_multipolygon_holes_contours(left_multipolygon),
                     right_multipolygon))
    assert result == subtract(
            left_multipolygon,
            reverse_multipolygon_holes_contours(right_multipolygon))
