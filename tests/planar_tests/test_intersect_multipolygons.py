from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_compounds_similar,
                         is_maybe_shaped,
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

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert is_maybe_shaped(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = intersect_multipolygons(multipolygon, multipolygon)

    assert are_compounds_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    left_right_union = unite_multipolygons(left_multipolygon,
                                           right_multipolygon)
    assert (not is_multipolygon(left_right_union)
            or are_compounds_similar(
                    intersect_multipolygons(left_right_union,
                                            left_multipolygon),
                    left_multipolygon))


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert result == intersect_multipolygons(right_multipolygon,
                                             left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_intersection = intersect_multipolygons(left_multipolygon,
                                                    mid_multipolygon)
    mid_right_intersection = intersect_multipolygons(mid_multipolygon,
                                                     right_multipolygon)
    assert (not is_multipolygon(left_mid_intersection)
            or not is_multipolygon(mid_right_intersection)
            or (intersect_multipolygons(left_mid_intersection,
                                        right_multipolygon)
                == intersect_multipolygons(left_multipolygon,
                                           mid_right_intersection)))


@given(strategies.multipolygons_triplets)
def test_difference_operand(multipolygons_triplet: MultipolygonsTriplet
                            ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_difference = subtract_multipolygons(left_multipolygon,
                                                 mid_multipolygon)
    left_right_intersection = intersect_multipolygons(left_multipolygon,
                                                      right_multipolygon)
    assert (not is_multipolygon(left_mid_difference)
            or not is_multipolygon(left_right_intersection)
            or (intersect_multipolygons(left_mid_difference,
                                        right_multipolygon)
                == subtract_multipolygons(left_right_intersection,
                                          mid_multipolygon)))


@given(strategies.multipolygons_triplets)
def test_distribution_over_union(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    mid_right_union = unite_multipolygons(mid_multipolygon, right_multipolygon)
    left_mid_intersection = intersect_multipolygons(left_multipolygon,
                                                    mid_multipolygon)
    left_right_intersection = intersect_multipolygons(left_multipolygon,
                                                      right_multipolygon)
    assert (not is_multipolygon(mid_right_union)
            or not is_multipolygon(left_mid_intersection)
            or not is_multipolygon(left_right_intersection)
            or (intersect_multipolygons(left_multipolygon, mid_right_union)
                == unite_multipolygons(left_mid_intersection,
                                       left_right_intersection)))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    left_right_difference = subtract_multipolygons(left_multipolygon,
                                                   right_multipolygon)
    assert (not is_multipolygon(left_right_difference)
            or are_compounds_similar(result,
                                     subtract_multipolygons(
                                             left_multipolygon,
                                             left_right_difference)))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = intersect_multipolygons(left_multipolygon, right_multipolygon)

    assert result == intersect_multipolygons(
            reverse_multipolygon(left_multipolygon), right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon, reverse_multipolygon(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_borders(left_multipolygon),
            right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_borders(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_holes(left_multipolygon), right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon, reverse_multipolygon_holes(right_multipolygon))
    assert result == intersect_multipolygons(
            reverse_multipolygon_holes_contours(left_multipolygon),
            right_multipolygon)
    assert result == intersect_multipolygons(
            left_multipolygon,
            reverse_multipolygon_holes_contours(right_multipolygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(intersect_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
