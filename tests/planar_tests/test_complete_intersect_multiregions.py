from hypothesis import given

from clipping.hints import Multiregion
from clipping.planar import (complete_intersect_multiregions,
                             intersect_multiregions)
from tests.utils import (MultiregionsPair,
                         are_compounds_similar,
                         compound_to_shaped,
                         is_holeless_compound,
                         is_multipolygon_similar_to_multiregion,
                         reverse_compound_coordinates,
                         reverse_multiregion,
                         reverse_multiregion_coordinates,
                         reverse_multiregion_regions)
from . import strategies


@given(strategies.multiregions_pairs)
def test_basic(multiregions_pair: MultiregionsPair) -> None:
    first, second = multiregions_pair

    result = complete_intersect_multiregions(first, second)

    assert is_holeless_compound(result)


@given(strategies.multiregions)
def test_idempotence(multiregion: Multiregion) -> None:
    result = complete_intersect_multiregions(multiregion, multiregion)

    assert is_multipolygon_similar_to_multiregion(result, multiregion)


@given(strategies.multiregions_pairs)
def test_commutativity(multiregions_pair: MultiregionsPair) -> None:
    first, second = multiregions_pair

    result = complete_intersect_multiregions(first, second)

    assert result == complete_intersect_multiregions(second, first)


@given(strategies.multiregions_pairs)
def test_connection_with_intersect(multiregions_pair: MultiregionsPair
                                   ) -> None:
    first, second = multiregions_pair

    result = complete_intersect_multiregions(first, second)

    assert compound_to_shaped(result) == intersect_multiregions(first, second)


@given(strategies.multiregions_pairs)
def test_reversals(multiregions_pair: MultiregionsPair) -> None:
    first, second = multiregions_pair

    result = complete_intersect_multiregions(first, second)

    assert result == complete_intersect_multiregions(
            first, reverse_multiregion(second))
    assert result == complete_intersect_multiregions(
            first, reverse_multiregion_regions(second))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_multiregions(
                    reverse_multiregion_coordinates(first),
                    reverse_multiregion_coordinates(second))))
