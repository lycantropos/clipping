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
    first, second = multipolygons_pair

    result = symmetric_subtract_multipolygons(first, second)

    assert is_maybe_shaped(result)


@given(strategies.multipolygons)
def test_self_inverse(multipolygon: Multipolygon) -> None:
    result = symmetric_subtract_multipolygons(multipolygon, multipolygon)

    assert is_empty(result)


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = symmetric_subtract_multipolygons(first, second)

    assert result == symmetric_subtract_multipolygons(second, first)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    first, second, third = multipolygons_triplet

    first_second_symmetric_difference = symmetric_subtract_multipolygons(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_multipolygons(
            second, third)
    assert (not is_multipolygon(first_second_symmetric_difference)
            or not is_multipolygon(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_multipolygons(
                            first_second_symmetric_difference, third),
                    symmetric_subtract_multipolygons(
                            first,
                            second_third_symmetric_difference)))


@given(strategies.multipolygons_triplets)
def test_repeated(multipolygons_triplet: MultipolygonsTriplet) -> None:
    first, second, third = multipolygons_triplet

    first_second_symmetric_difference = symmetric_subtract_multipolygons(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_multipolygons(
            second, third)
    assert (not is_multipolygon(first_second_symmetric_difference)
            or not is_multipolygon(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_multipolygons(
                            first_second_symmetric_difference,
                            second_third_symmetric_difference),
                    symmetric_subtract_multipolygons(first,
                                                     third)))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = symmetric_subtract_multipolygons(first, second)

    first_second_difference = subtract_multipolygons(first, second)
    first_second_union = unite_multipolygons(first, second)
    second_first_difference = subtract_multipolygons(second, first)
    second_first_intersection = intersect_multipolygons(second, first)
    assert (not is_multipolygon(first_second_difference)
            or not is_multipolygon(second_first_difference)
            or result == unite_multipolygons(first_second_difference,
                                             second_first_difference))
    assert (not is_multipolygon(first_second_union)
            or not is_multipolygon(second_first_intersection)
            or result == subtract_multipolygons(first_second_union,
                                                second_first_intersection))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = symmetric_subtract_multipolygons(first, second)

    assert are_compounds_similar(
            result,
            symmetric_subtract_multipolygons(first,
                                             reverse_multipolygon(second)))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    first, reverse_multipolygon_borders(second)))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    first, reverse_multipolygon_holes(second)))
    assert are_compounds_similar(
            result, symmetric_subtract_multipolygons(
                    first, reverse_multipolygon_holes_contours(second)))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(symmetric_subtract_multipolygons(
                    reverse_multipolygon_coordinates(first),
                    reverse_multipolygon_coordinates(second))))
