from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import unite
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon)
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
