from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import (intersect,
                             subtract,
                             unite)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon,
                         reverse_polygons)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = unite(left_multipolygon, right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = unite(multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_neutral_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = unite(empty_multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_neutral_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = unite(multipolygon, empty_multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = unite(left_multipolygon, intersect(left_multipolygon,
                                                right_multipolygon))

    assert are_multipolygons_similar(result, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = unite(left_multipolygon, right_multipolygon)

    assert result == unite(right_multipolygon, left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = unite(unite(left_multipolygon, mid_multipolygon),
                   right_multipolygon)

    assert are_multipolygons_similar(result,
                                     unite(left_multipolygon,
                                           unite(mid_multipolygon,
                                                 right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_difference_operand(multipolygons_triplet: MultipolygonsTriplet
                            ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = unite(subtract(left_multipolygon, mid_multipolygon),
                   right_multipolygon)

    assert are_multipolygons_similar(result,
                                     subtract(unite(left_multipolygon,
                                                    right_multipolygon),
                                              subtract(mid_multipolygon,
                                                       right_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_distribution_over_intersection(
        multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = unite(left_multipolygon, intersect(mid_multipolygon,
                                                right_multipolygon))

    assert are_multipolygons_similar(result,
                                     intersect(unite(left_multipolygon,
                                                     mid_multipolygon),
                                               unite(left_multipolygon,
                                                     right_multipolygon)))


@given(strategies.multipolygons_pairs)
def test_reversed(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = unite(left_multipolygon, right_multipolygon)

    assert result == unite(left_multipolygon[::-1], right_multipolygon)
    assert result == unite(left_multipolygon, right_multipolygon[::-1])


@given(strategies.multipolygons_pairs)
def test_reversed_polygons(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = unite(left_multipolygon, right_multipolygon)

    assert are_multipolygons_similar(result,
                                     unite(reverse_polygons(left_multipolygon),
                                           right_multipolygon))
    assert are_multipolygons_similar(
            result,
            unite(left_multipolygon, reverse_polygons(right_multipolygon)))
