from hypothesis import given

from clipping.planar import (intersect,
                             subtract,
                             symmetric_subtract,
                             unite)
from tests.utils import (Multipolygon,
                         MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_multipolygons_similar,
                         is_multipolygon)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(left_multipolygon, right_multipolygon)

    assert is_multipolygon(result)


@given(strategies.multipolygons)
def test_self_inverse(multipolygon: Multipolygon) -> None:
    result = symmetric_subtract(multipolygon, multipolygon)

    assert not result


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_neutral_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = symmetric_subtract(empty_multipolygon, multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_neutral_element(
        empty_multipolygon_with_multipolygon: MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = symmetric_subtract(multipolygon, empty_multipolygon)

    assert are_multipolygons_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(left_multipolygon, right_multipolygon)

    assert result == symmetric_subtract(right_multipolygon, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_equivalent_using_union_of_differences(
        multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(subtract(left_multipolygon,
                                         right_multipolygon),
                                subtract(right_multipolygon,
                                         left_multipolygon))

    assert result == symmetric_subtract(left_multipolygon, right_multipolygon)


@given(strategies.multipolygons_pairs)
def test_equivalent_using_difference_of_union_and_intersection(
        multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(left_multipolygon, right_multipolygon)

    assert result == subtract(unite(left_multipolygon, right_multipolygon),
                              intersect(right_multipolygon, left_multipolygon))


@given(strategies.multipolygons_pairs)
def test_expressing_union_as_symmetric_difference(
        multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract(symmetric_subtract(left_multipolygon,
                                                   right_multipolygon),
                                intersect(left_multipolygon,
                                          right_multipolygon))

    assert result == unite(left_multipolygon, right_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    result = symmetric_subtract(symmetric_subtract(left_multipolygon,
                                                   mid_multipolygon),
                                right_multipolygon)

    assert result == symmetric_subtract(left_multipolygon,
                                        symmetric_subtract(mid_multipolygon,
                                                           right_multipolygon))


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
