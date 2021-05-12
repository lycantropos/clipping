from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (complete_intersect_multipolygons,
                             intersect_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         are_compounds_similar,
                         compound_to_shaped,
                         is_compound,
                         is_multipolygon,
                         reverse_compound_coordinates,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours)
from . import strategies


@given(strategies.multipolygons_pairs)
def test_basic(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = complete_intersect_multipolygons(first, second)

    assert is_compound(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = complete_intersect_multipolygons(multipolygon, multipolygon)

    assert are_compounds_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    first_second_union = unite_multipolygons(first, second)

    assert (not is_multipolygon(first_second_union)
            or are_compounds_similar(
                    first,
                    complete_intersect_multipolygons(first_second_union,
                                                     first)))


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = complete_intersect_multipolygons(first, second)

    assert result == complete_intersect_multipolygons(second, first)


@given(strategies.multipolygons_pairs)
def test_connection_with_intersect(multipolygons_pair: MultipolygonsPair
                                   ) -> None:
    first, second = multipolygons_pair

    result = complete_intersect_multipolygons(first, second)

    assert compound_to_shaped(result) == intersect_multipolygons(first, second)


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = complete_intersect_multipolygons(first, second)

    assert result == complete_intersect_multipolygons(
            first, reverse_multipolygon(second))
    assert result == complete_intersect_multipolygons(
            first, reverse_multipolygon_borders(second))
    assert result == complete_intersect_multipolygons(
            first, reverse_multipolygon_holes(second))
    assert result == complete_intersect_multipolygons(
            first, reverse_multipolygon_holes_contours(second))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_multipolygons(
                    reverse_multipolygon_coordinates(first),
                    reverse_multipolygon_coordinates(second))))
