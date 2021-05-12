from ground.hints import Multipolygon
from hypothesis import given

from clipping.planar import (intersect_multipolygons,
                             subtract_multipolygons,
                             symmetric_subtract_multipolygons,
                             unite_multipolygons)
from tests.utils import (MultipolygonsPair,
                         MultipolygonsTriplet,
                         are_compounds_similar,
                         is_multipolygon,
                         is_shaped,
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

    result = unite_multipolygons(first, second)

    assert is_shaped(result)


@given(strategies.multipolygons)
def test_idempotence(multipolygon: Multipolygon) -> None:
    result = unite_multipolygons(multipolygon, multipolygon)

    assert are_compounds_similar(result, multipolygon)


@given(strategies.multipolygons_pairs)
def test_absorption_identity(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    first_second_intersection = intersect_multipolygons(first, second)
    assert (not is_multipolygon(first_second_intersection)
            or are_compounds_similar(
                    unite_multipolygons(first, first_second_intersection),
                    first))


@given(strategies.multipolygons_pairs)
def test_commutativity(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = unite_multipolygons(first, second)

    assert result == unite_multipolygons(second, first)


@given(strategies.multipolygons_triplets)
def test_associativity(multipolygons_triplet: MultipolygonsTriplet) -> None:
    first, second, third = multipolygons_triplet

    first_second_union = unite_multipolygons(first, second)
    second_third_union = unite_multipolygons(second, third)
    assert (not is_multipolygon(first_second_union)
            or not is_multipolygon(second_third_union)
            or are_compounds_similar(
                    unite_multipolygons(first_second_union, third),
                    unite_multipolygons(first, second_third_union)))


@given(strategies.multipolygons_triplets)
def test_difference_operand(multipolygons_triplet: MultipolygonsTriplet
                            ) -> None:
    first, second, third = multipolygons_triplet

    first_second_difference = subtract_multipolygons(first, second)
    first_third_union = unite_multipolygons(first, third)
    second_third_difference = subtract_multipolygons(second, third)
    assert (not is_multipolygon(first_second_difference)
            or not is_multipolygon(first_third_union)
            or not is_multipolygon(second_third_difference)
            or are_compounds_similar(
                    unite_multipolygons(first_second_difference, third),
                    subtract_multipolygons(first_third_union,
                                           second_third_difference)))


@given(strategies.multipolygons_triplets)
def test_distribution_over_intersection(multipolygons_triplet
                                        : MultipolygonsTriplet) -> None:
    first, second, third = multipolygons_triplet

    second_third_intersection = intersect_multipolygons(second, third)
    first_second_union = unite_multipolygons(first, second)
    first_third_union = unite_multipolygons(first, third)
    assert (not is_multipolygon(second_third_intersection)
            or not is_multipolygon(first_second_union)
            or not is_multipolygon(first_third_union)
            or are_compounds_similar(
                    unite_multipolygons(first, second_third_intersection),
                    intersect_multipolygons(first_second_union,
                                            first_third_union)))


@given(strategies.multipolygons_pairs)
def test_equivalents(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = unite_multipolygons(first, second)

    first_second_symmetric_difference = symmetric_subtract_multipolygons(
            first, second)
    first_second_intersection = intersect_multipolygons(first, second)
    assert (not is_multipolygon(first_second_symmetric_difference)
            or not is_multipolygon(first_second_intersection)
            or result == symmetric_subtract_multipolygons(
                    first_second_symmetric_difference,
                    first_second_intersection))


@given(strategies.multipolygons_pairs)
def test_reversals(multipolygons_pair: MultipolygonsPair) -> None:
    first, second = multipolygons_pair

    result = unite_multipolygons(first, second)

    assert are_compounds_similar(
            result, unite_multipolygons(first, reverse_multipolygon(second)))
    assert are_compounds_similar(
            result, unite_multipolygons(first,
                                        reverse_multipolygon_borders(second)))
    assert are_compounds_similar(
            result, unite_multipolygons(first,
                                        reverse_multipolygon_holes(second)))
    assert are_compounds_similar(
            result, unite_multipolygons(
                    first, reverse_multipolygon_holes_contours(second)))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(unite_multipolygons(
                    reverse_multipolygon_coordinates(first),
                    reverse_multipolygon_coordinates(second))))
