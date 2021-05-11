from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_compounds_similar,
                         is_empty,
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

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert is_maybe_shaped(result)


@given(strategies.multipolygons)
def test_self_inverse(multipolygon: Multipolygon) -> None:
    result = symmetric_subtract_multipolygons(multipolygon, multipolygon)

    assert is_empty(result)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert result == symmetric_subtract_multipolygons(right_multipolygon,
                                                      left_multipolygon)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_symmetric_difference = symmetric_subtract_multipolygons(
            left_multipolygon, mid_multipolygon)
    mid_right_symmetric_difference = symmetric_subtract_multipolygons(
            mid_multipolygon, right_multipolygon)
    assert (not is_multipolygon(left_mid_symmetric_difference)
            or not is_multipolygon(mid_right_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_multipolygons(
                            left_mid_symmetric_difference, right_multipolygon),
                    symmetric_subtract_multipolygons(
                            left_multipolygon,
                            mid_right_symmetric_difference)))


@given(strategies.multipolygons_triplets)
def test_repeated(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_symmetric_difference = symmetric_subtract_multipolygons(
            left_multipolygon, mid_multipolygon)
    mid_right_symmetric_difference = symmetric_subtract_multipolygons(
            mid_multipolygon, right_multipolygon)
    assert (not is_multipolygon(left_mid_symmetric_difference)
            or not is_multipolygon(mid_right_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_multipolygons(
                            left_mid_symmetric_difference,
                            mid_right_symmetric_difference),
                    symmetric_subtract_multipolygons(left_multipolygon,
                                                     right_multipolygon)))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    left_right_difference = subtract_multipolygons(left_multipolygon,
                                                   right_multipolygon)
    left_right_union = unite_multipolygons(left_multipolygon,
                                           right_multipolygon)
    right_left_difference = subtract_multipolygons(right_multipolygon,
                                                   left_multipolygon)
    right_left_intersection = intersect_multipolygons(right_multipolygon,
                                                      left_multipolygon)
    assert (not is_multipolygon(left_right_difference)
            or not is_multipolygon(right_left_difference)
            or result == unite_multipolygons(left_right_difference,
                                             right_left_difference))
    assert (not is_multipolygon(left_right_union)
            or not is_multipolygon(right_left_intersection)
            or result == subtract_multipolygons(left_right_union,
                                                right_left_intersection))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = symmetric_subtract_multipolygons(left_multipolygon,
                                              right_multipolygon)

    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    reverse_multipolygon(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(left_multipolygon,
                                             reverse_multipolygon(
                                                     right_multipolygon)))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(
                    reverse_multipolygon_borders(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_borders(right_multipolygon)))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(
                    reverse_multipolygon_holes(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_holes(right_multipolygon)))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    reverse_multipolygon_holes_contours(left_multipolygon),
                    right_multipolygon))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    left_multipolygon,
                    reverse_multipolygon_holes_contours(right_multipolygon)))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(symmetric_subtract_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
