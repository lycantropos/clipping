from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (complete_intersect_multipolygons,
                             complete_intersect_polygon_with_multipolygon,
                             intersect_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         are_compounds_similar,
                         is_compound,
                         is_mix,
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
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert is_compound(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = complete_intersect_multipolygons(multipolygon, multipolygon)

    assert are_compounds_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    multipolygons_union = unite_multipolygons(left_multipolygon,
                                              right_multipolygon)
    result = ((complete_intersect_multipolygons
               if is_multipolygon(multipolygons_union)
               else complete_intersect_polygon_with_multipolygon)
              (multipolygons_union, left_multipolygon))

    assert are_compounds_similar(left_multipolygon, result)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert result == complete_intersect_multipolygons(right_multipolygon,
                                                      left_multipolygon)


@given(strategies.multipolygons_pairs)
def test_connection_with_intersect(multipolygons_pair: MultipolygonsPair
                                   ) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert (result.shaped
            if is_mix(result)
            else result) == intersect_multipolygons(left_multipolygon,
                                                    right_multipolygon)


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = complete_intersect_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert result == complete_intersect_multipolygons(
            reverse_multipolygon(left_multipolygon), right_multipolygon)
    assert result == complete_intersect_multipolygons(
            left_multipolygon, reverse_multipolygon(right_multipolygon))
    assert result == complete_intersect_multipolygons(
            reverse_multipolygon_borders(left_multipolygon),
            right_multipolygon)
    assert result == complete_intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_borders(right_multipolygon))
    assert result == complete_intersect_multipolygons(
            reverse_multipolygon_holes(left_multipolygon),
            right_multipolygon)
    assert result == complete_intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_holes(right_multipolygon))
    assert result == complete_intersect_multipolygons(
            reverse_multipolygon_holes_contours(left_multipolygon),
            right_multipolygon)
    assert result == complete_intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_holes_contours(right_multipolygon))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
