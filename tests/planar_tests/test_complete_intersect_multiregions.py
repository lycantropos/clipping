from hypothesis import given

from clipping.hints import Multiregion
from clipping.planar import (complete_intersect_multiregions,
                             intersect_multiregions)
from tests.utils import (MultiregionsPair,
                         holeless_mix_similar_to_multiregion,
                         is_holeless_mix,
                         is_holeless_mix_empty,
                         reverse_multiregion,
                         reverse_multiregion_regions)
from . import strategies


@given(strategies.multiregions_pairs)
def test_basic(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = complete_intersect_multiregions(left_multiregion,
                                             right_multiregion)

    assert is_holeless_mix(result)


@given(strategies.multiregions)
def test_idempotence(multiregion: Multiregion) -> None:
    result = complete_intersect_multiregions(multiregion, multiregion)

    assert holeless_mix_similar_to_multiregion(result, multiregion)


@given(strategies.empty_multiregions_with_multiregions)
def test_left_absorbing_element(empty_multiregion_with_multiregion
                                : MultiregionsPair) -> None:
    empty_multiregion, multiregion = empty_multiregion_with_multiregion

    result = complete_intersect_multiregions(empty_multiregion, multiregion)

    assert is_holeless_mix_empty(result)


@given(strategies.empty_multiregions_with_multiregions)
def test_right_absorbing_element(empty_multiregion_with_multiregion
                                 : MultiregionsPair) -> None:
    empty_multiregion, multiregion = empty_multiregion_with_multiregion

    result = complete_intersect_multiregions(multiregion, empty_multiregion)

    assert is_holeless_mix_empty(result)


@given(strategies.multiregions_pairs)
def test_commutativity(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = complete_intersect_multiregions(left_multiregion,
                                             right_multiregion)

    assert result == complete_intersect_multiregions(right_multiregion,
                                                     left_multiregion)


@given(strategies.multiregions_pairs)
def test_connection_with_intersect(multiregions_pair: MultiregionsPair
                                   ) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = complete_intersect_multiregions(left_multiregion,
                                             right_multiregion)

    _, _, multiregion = result
    assert multiregion == intersect_multiregions(left_multiregion,
                                                 right_multiregion)


@given(strategies.multiregions_pairs)
def test_reversals(multiregions_pair: MultiregionsPair) -> None:
    left_multiregion, right_multiregion = multiregions_pair

    result = complete_intersect_multiregions(left_multiregion,
                                             right_multiregion)

    assert result == complete_intersect_multiregions(
            reverse_multiregion(left_multiregion), right_multiregion)
    assert result == complete_intersect_multiregions(
            left_multiregion, reverse_multiregion(right_multiregion))
    assert result == complete_intersect_multiregions(
            reverse_multiregion_regions(left_multiregion), right_multiregion)
    assert result == complete_intersect_multiregions(
            left_multiregion, reverse_multiregion_regions(right_multiregion))
