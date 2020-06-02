from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import (complete_intersect,
                             intersect,
                             unite)
from tests.utils import (MultipolygonsPair,
                         is_mix,
                         mix_similar_to_multipolygon,
                         reverse_polygons)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect(left_multipolygon, right_multipolygon)

    assert is_mix(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = complete_intersect(multipolygon, multipolygon)

    assert mix_similar_to_multipolygon(result, multipolygon)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_left_absorbing_element(empty_multipolygon_with_multipolygon
                                : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = complete_intersect(empty_multipolygon, multipolygon)

    assert not any(result)


@given(strategies.empty_multipolygons_with_multipolygons)
def test_right_absorbing_element(empty_multipolygon_with_multipolygon
                                 : MultipolygonsPair) -> None:
    empty_multipolygon, multipolygon = empty_multipolygon_with_multipolygon

    result = complete_intersect(multipolygon, empty_multipolygon)

    assert not any(result)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect(left_multipolygon, unite(left_multipolygon,
                                                         right_multipolygon))

    assert mix_similar_to_multipolygon(result, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect(left_multipolygon, right_multipolygon)

    assert result == complete_intersect(right_multipolygon, left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_connection_with_intersect(multipolygons_pair: MultipolygonsPair
                                   ) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect(left_multipolygon, right_multipolygon)

    _, _, multipolygon = result
    assert multipolygon == intersect(left_multipolygon, right_multipolygon)


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect(left_multipolygon, right_multipolygon)

    assert result == complete_intersect(left_multipolygon[::-1],
                                        right_multipolygon)
    assert result == complete_intersect(left_multipolygon,
                                        right_multipolygon[::-1])
    assert result == complete_intersect(reverse_polygons(left_multipolygon),
                                        right_multipolygon)
    assert result == complete_intersect(left_multipolygon,
                                        reverse_polygons(right_multipolygon))
