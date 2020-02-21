from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import (intersect,
                             subtract,
                             unite)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect(left_multipolygon, right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = intersect(multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_absorbing_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = intersect(empty_multipolygon, multipolygon)

    assert not result


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_absorbing_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = intersect(multipolygon, empty_multipolygon)

    assert not result


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect(left_multipolygon, unite(left_multipolygon,
                                                right_multipolygon))

    assert are_multipolygons_similar(result, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect(left_multipolygon, right_multipolygon)

    assert result == intersect(right_multipolygon, left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect(intersect(left_multipolygon, mid_multipolygon),
                       right_multipolygon)

    assert result == intersect(left_multipolygon,
                               intersect(mid_multipolygon, right_multipolygon))


@given(strategies.multipolygons_triplets)
def test_difference_operand(multipolygons_triplet: MultipolygonsTriplet
                            ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect(subtract(left_multipolygon, mid_multipolygon),
                       right_multipolygon)

    assert result == subtract(intersect(left_multipolygon, right_multipolygon),
                              mid_multipolygon)


@given(strategies.multipolygons_triplets)
def test_distribution_over_union(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = intersect(left_multipolygon, unite(mid_multipolygon,
                                                right_multipolygon))

    assert result == unite(intersect(left_multipolygon, mid_multipolygon),
                           intersect(left_multipolygon, right_multipolygon))
