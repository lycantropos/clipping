from typing import List

from hypothesis import given

from clipping.hints import Multipolygon
from clipping.planar import (complete_intersect,
                             intersect,
                             unite)
from tests.utils import (MultipolygonsPair,
                         are_mixes_similar,
                         is_mix,
                         mix_similar_to_multipolygon,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours)
from . import strategies


@given(strategies.multipolygons_lists)
def test_basic(multipolygons: List[Multipolygon]) -> None:
    result = complete_intersect(*multipolygons)

    assert is_mix(result)


@given(strategies.empty_multipolygons_lists)
def test_degenerate(multipolygons: List[Multipolygon]) -> None:
    assert not any(complete_intersect(*multipolygons))


@given(strategies.multipolygons)
def test_self(multipolygon: Multipolygon) -> None:
    assert complete_intersect(multipolygon) == ([], [], multipolygon)
    assert mix_similar_to_multipolygon(complete_intersect(multipolygon,
                                                          multipolygon),
                                       multipolygon)


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


@given(strategies.multipolygons_lists)
def test_connection_with_intersect(multipolygons: List[Multipolygon]) -> None:
    result = complete_intersect(*multipolygons)

    _, _, multipolygon = result
    assert multipolygon == intersect(*multipolygons)


@given(strategies.non_empty_multipolygons_lists)
def test_reversals(multipolygons: List[Multipolygon]) -> None:
    first_multipolygon, *rest_multipolygons = multipolygons

    result = complete_intersect(first_multipolygon, *rest_multipolygons)

    assert are_mixes_similar(
            result,
            complete_intersect(reverse_multipolygon(first_multipolygon),
                               *rest_multipolygons))
    assert are_mixes_similar(
            result,
            complete_intersect(
                    reverse_multipolygon_borders(first_multipolygon),
                    *rest_multipolygons))
    assert are_mixes_similar(
            result,
            complete_intersect(reverse_multipolygon_holes(first_multipolygon),
                               *rest_multipolygons))
    assert are_mixes_similar(
            result,
            complete_intersect(
                    reverse_multipolygon_holes_contours(first_multipolygon),
                    *rest_multipolygons))
