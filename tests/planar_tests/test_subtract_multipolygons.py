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
    first, second = multipolygons_pair

    result = subtract_multipolygons(first, second)

    assert is_maybe_shaped(result)


@given(strategies.multipolygons_pairs)
def test_commutative_case(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = subtract_multipolygons(first, second)

    assert equivalence(result == subtract_multipolygons(second, first),
                       are_compounds_similar(first, second))


@given(strategies.multipolygons_triplets)
def test_difference_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                               ) -> None:
    first, second, third = multipolygons_triplet

    first_third_intersection = intersect_multipolygons(first, third)
    first_second_difference = subtract_multipolygons(first, second)
    second_third_difference = subtract_multipolygons(second, third)
    assert (not is_multipolygon(first_second_difference)
            or not is_multipolygon(first_third_intersection)
            or not is_multipolygon(second_third_difference)
            or are_compounds_similar(
                    subtract_multipolygons(first, second_third_difference),
                    unite_multipolygons(first_second_difference,
                                        first_third_intersection)))


@given(strategies.multipolygons_triplets)
def test_intersection_minuend(multipolygons_triplet: MultipolygonsTriplet
                              ) -> None:
    first, second, third = multipolygons_triplet

    first_second_intersection = intersect_multipolygons(first, second)
    second_third_difference = subtract_multipolygons(second, third)
    assert (not is_multipolygon(first_second_intersection)
            or not is_multipolygon(second_third_difference)
            or (subtract_multipolygons(first_second_intersection, third)
                == intersect_multipolygons(first, second_third_difference)))


@given(strategies.multipolygons_triplets)
def test_intersection_subtrahend(multipolygons_triplet: MultipolygonsTriplet
                                 ) -> None:
    first, second, third = multipolygons_triplet

    first_second_difference = subtract_multipolygons(first, second)
    first_third_difference = subtract_multipolygons(first, third)
    second_third_intersection = intersect_multipolygons(second, third)
    assert (not is_multipolygon(first_second_difference)
            or not is_multipolygon(first_third_difference)
            or not is_multipolygon(second_third_intersection)
            or are_compounds_similar(
                    subtract_multipolygons(first, second_third_intersection),
                    unite_multipolygons(first_second_difference,
                                        first_third_difference)))


@given(strategies.multipolygons_triplets)
def test_union_subtrahend(multipolygons_triplet: MultipolygonsTriplet) -> None:
    first, second, third = multipolygons_triplet

    first_second_difference = subtract_multipolygons(first, second)
    first_third_difference = subtract_multipolygons(first, third)
    second_third_union = unite_multipolygons(second, third)
    assert (not is_multipolygon(first_second_difference)
            or not is_multipolygon(first_third_difference)
            or not is_multipolygon(second_third_union)
            or are_compounds_similar(
                    subtract_multipolygons(first, second_third_union),
                    intersect_multipolygons(first_second_difference,
                                            first_third_difference)))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = subtract_multipolygons(first, second)

    assert are_compounds_similar(
            result, subtract_multipolygons(reverse_multipolygon(first),
                                           second))
    assert result == subtract_multipolygons(first,
                                            reverse_multipolygon(second))
    assert are_compounds_similar(
            result, subtract_multipolygons(reverse_multipolygon_borders(first),
                                           second))
    assert result == subtract_multipolygons(
            first, reverse_multipolygon_borders(second))
    assert are_compounds_similar(
            result, subtract_multipolygons(reverse_multipolygon_holes(first),
                                           second))
    assert result == subtract_multipolygons(first,
                                            reverse_multipolygon_holes(second))
    assert are_compounds_similar(
            result,
            subtract_multipolygons(reverse_multipolygon_holes_contours(first),
                                   second))
    assert result == subtract_multipolygons(
            first, reverse_multipolygon_holes_contours(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_multipolygons(
                    reverse_multipolygon_coordinates(first),
                    reverse_multipolygon_coordinates(second))))
