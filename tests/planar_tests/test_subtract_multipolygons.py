from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_compounds_similar,
                         equivalence,
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

    result = subtract_multipolygons(left_multipolygon, right_multipolygon)

    assert is_maybe_shaped(result)


@given(strategies.multipolygons_pairs)
def test_commutative_case(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract_multipolygons(left_multipolygon, right_multipolygon)

    assert equivalence(result == subtract_multipolygons(right_multipolygon,
                                                        left_multipolygon),
                       are_compounds_similar(left_multipolygon,
                                             right_multipolygon))


@given(strategies.multipolygons_triplets)
def test_difference_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                               ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_right_intersection = intersect_multipolygons(left_multipolygon,
                                                      right_multipolygon)
    left_mid_difference = subtract_multipolygons(left_multipolygon,
                                                 mid_multipolygon)
    mid_right_difference = subtract_multipolygons(mid_multipolygon,
                                                  right_multipolygon)
    assert (not is_multipolygon(left_mid_difference)
            or not is_multipolygon(left_right_intersection)
            or not is_multipolygon(mid_right_difference)
            or are_compounds_similar(
                    subtract_multipolygons(left_multipolygon,
                                           mid_right_difference),
                    unite_multipolygons(left_mid_difference,
                                        left_right_intersection)))


@given(strategies.multipolygons_triplets)
def test_intersection_minuend(multipolygons_triplet: MultipolygonsTriplet
                              ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_intersection = intersect_multipolygons(left_multipolygon,
                                                    mid_multipolygon)
    mid_right_difference = subtract_multipolygons(mid_multipolygon,
                                                  right_multipolygon)
    assert (not is_multipolygon(left_mid_intersection)
            or not is_multipolygon(mid_right_difference)
            or (subtract_multipolygons(left_mid_intersection,
                                       right_multipolygon)
                == intersect_multipolygons(left_multipolygon,
                                           mid_right_difference)))


@given(strategies.multipolygons_triplets)
def test_intersection_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_difference = subtract_multipolygons(left_multipolygon,
                                                 mid_multipolygon)
    left_right_difference = subtract_multipolygons(left_multipolygon,
                                                   right_multipolygon)
    mid_right_intersection = intersect_multipolygons(mid_multipolygon,
                                                     right_multipolygon)
    assert (not is_multipolygon(left_mid_difference)
            or not is_multipolygon(left_right_difference)
            or not is_multipolygon(mid_right_intersection)
            or are_compounds_similar(
                    subtract_multipolygons(left_multipolygon,
                                           mid_right_intersection),
                    unite_multipolygons(left_mid_difference,
                                        left_right_difference)))


@given(strategies.multipolygons_triplets)
def test_union_subtrahend(multipolygons_triplet: MultipolygonsTriplet) -> None:
    (left_multipolygon, mid_multipolygon,
     right_multipolygon) = multipolygons_triplet

    left_mid_difference = subtract_multipolygons(left_multipolygon,
                                                 mid_multipolygon)
    left_right_difference = subtract_multipolygons(left_multipolygon,
                                                   right_multipolygon)
    mid_right_union = unite_multipolygons(mid_multipolygon, right_multipolygon)
    assert (not is_multipolygon(left_mid_difference)
            or not is_multipolygon(left_right_difference)
            or not is_multipolygon(mid_right_union)
            or are_compounds_similar(
                    subtract_multipolygons(left_multipolygon, mid_right_union),
                    intersect_multipolygons(left_mid_difference,
                                            left_right_difference)))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    left_multipolygon, right_multipolygon = multipolygons_pair

    result = subtract_multipolygons(left_multipolygon, right_multipolygon)

    assert are_compounds_similar(
            result,
            subtract_multipolygons(reverse_multipolygon(left_multipolygon),
                                   right_multipolygon))
    assert result == subtract_multipolygons(
            left_multipolygon, reverse_multipolygon(right_multipolygon))
    assert are_compounds_similar(
            result, subtract_multipolygons(
                    reverse_multipolygon_borders(left_multipolygon),
                    right_multipolygon))
    assert result == subtract_multipolygons(
            left_multipolygon,
            reverse_multipolygon_borders(right_multipolygon))
    assert are_compounds_similar(
            result, subtract_multipolygons(
                    reverse_multipolygon_holes(left_multipolygon),
                    right_multipolygon))
    assert result == subtract_multipolygons(
            left_multipolygon, reverse_multipolygon_holes(right_multipolygon))
    assert are_compounds_similar(
            result,
            subtract_multipolygons(
                    reverse_multipolygon_holes_contours(left_multipolygon),
                    right_multipolygon))
    assert result == subtract_multipolygons(
            left_multipolygon,
            reverse_multipolygon_holes_contours(right_multipolygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_multipolygons(
                    reverse_multipolygon_coordinates(left_multipolygon),
                    reverse_multipolygon_coordinates(right_multipolygon))))
