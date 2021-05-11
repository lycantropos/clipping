from hypothesis import given

from clipping.hints import Multiregion
from clipping.planar import intersect_multiregions
from tests.utils import (MultiregionsPair,
                         are_compounds_similar,
                         is_holeless_compound,
                         is_multipolygon_similar_to_multiregion,
                         reverse_compound_coordinates,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions)
from . import strategies


@given(strategies.multiregions_pairs)
def test_basic(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    assert is_holeless_compound(result)


@given(strategies.multiregions)
def test_idempotence(multiregion: Multiregion) -> None:
    result = intersect_multiregions(multiregion, multiregion)

    assert is_multipolygon_similar_to_multiregion(result, multiregion)


@given(strategies.multiregions_pairs)
def test_commutativity(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = intersect_multiregions(left_multiregion, right_multiregion)

    assert result == intersect_multiregions(right_multiregion,
                                            left_multiregion)


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
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(intersect_multiregions(
                    reverse_multiregion_coordinates(left_multiregion),
                    reverse_multiregion_coordinates(right_multiregion))))
