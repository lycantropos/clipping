from hypothesis import given

from clipping.hints import Multiregion
from clipping.planar import (intersect_multipolygons,
                             intersect_multiregions,
                             subtract_multipolygons)
from tests.utils import (MultiregionsPair,
                         MultiregionsTriplet,
                         are_multiregions_similar,
                         is_multiregion,
                         multipolygon_to_multiregion,
                         multiregion_to_multipolygon,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions)
from . import strategies


@given(strategies.multiregions_pairs)
def test_basic(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    assert is_multiregion(result)


@given(strategies.multiregions)
def test_idempotence(multiregion: Multiregion) -> None:
    result = intersect_multiregions(multiregion, multiregion)

    assert are_multiregions_similar(result, multiregion)


@given(strategies.empty_multiregions_with_multiregions)
def test_left_absorbing_element(empty_multiregion_with_multiregion
                                : MultiregionsPair) -> None:
    empty_multiregion, multiregion = empty_multiregion_with_multiregion

    result = intersect_multiregions(empty_multiregion, multiregion)

    assert not result


@given(strategies.empty_multiregions_with_multiregions)
def test_right_absorbing_element(empty_multiregion_with_multiregion
                                 : MultiregionsPair) -> None:
    empty_multiregion, multiregion = empty_multiregion_with_multiregion

    result = intersect_multiregions(multiregion, empty_multiregion)

    assert not result


@given(strategies.multiregions_pairs)
def test_commutativity(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    assert result == intersect_multiregions(right_multiregion,
                                            left_multiregion)


@given(strategies.multiregions_triplets)
def test_associativity(multiregions_triplet: MultiregionsTriplet) -> None:
    (left_multiregion, mid_multiregion,
     right_multiregion) = multiregions_triplet

    result = intersect_multiregions(
            intersect_multiregions(left_multiregion, mid_multiregion),
            right_multiregion)

    assert result == intersect_multiregions(left_multiregion,
                                            intersect_multiregions(
                                                    mid_multiregion,
                                                    right_multiregion))


@given(strategies.multiregions_pairs)
def test_equivalents(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    left_multipolygon = multiregion_to_multipolygon(left_multiregion)
    right_multipolygon = multiregion_to_multipolygon(right_multiregion)
    assert are_multiregions_similar(
            result,
            multipolygon_to_multiregion(subtract_multipolygons(
                    left_multipolygon,
                    subtract_multipolygons(left_multipolygon,
                                           right_multipolygon))))
    assert are_multiregions_similar(
            result,
            multipolygon_to_multiregion(intersect_multipolygons(
                    left_multipolygon, right_multipolygon)))


@given(strategies.multiregions_pairs)
def test_reversals(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    assert result == intersect_multiregions(
            reverse_multiregion(left_multiregion), right_multiregion)
    assert result == intersect_multiregions(
            left_multiregion, reverse_multiregion(right_multiregion))
    assert result == intersect_multiregions(
            reverse_multiregion_regions(left_multiregion), right_multiregion)
    assert result == intersect_multiregions(
            left_multiregion, reverse_multiregion_regions(right_multiregion))
    assert are_multiregions_similar(
            result,
            reverse_multiregion_coordinates(intersect_multiregions(
                    reverse_multiregion_coordinates(left_multiregion),
                    reverse_multiregion_coordinates(right_multiregion))))
