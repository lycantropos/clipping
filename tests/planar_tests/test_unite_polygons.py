from ground.hints import Polygon
from hypothesis import given

from clipping.planar import (intersect_polygons,
                             subtract_polygons,
                             symmetric_subtract_polygons,
                             unite_polygons)
from tests.utils import (PolygonsPair,
                         PolygonsTriplet,
                         are_compounds_similar,
                         is_polygon,
                         is_shaped,
                         reverse_compound_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours)
from . import strategies


@given(strategies.polygons_pairs)
def test_basic(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = unite_polygons(first, second)

    assert is_shaped(result)


@given(strategies.polygons)
def test_idempotence(polygon: Polygon) -> None:
    result = unite_polygons(polygon, polygon)

    assert are_compounds_similar(result, polygon)


@given(strategies.polygons_pairs)
def test_absorption_identity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    first_second_intersection = intersect_polygons(first, second)
    assert (not is_polygon(first_second_intersection)
            or are_compounds_similar(
                    unite_polygons(first, first_second_intersection), first
            ))


@given(strategies.polygons_pairs)
def test_commutativity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = unite_polygons(first, second)

    assert result == unite_polygons(second, first)


@given(strategies.polygons_triplets)
def test_associativity(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_union = unite_polygons(first, second)
    second_third_union = unite_polygons(second, third)
    assert (not is_polygon(first_second_union)
            or not is_polygon(second_third_union)
            or are_compounds_similar(
                    unite_polygons(first_second_union, third),
                    unite_polygons(first, second_third_union)
            ))


@given(strategies.polygons_triplets)
def test_difference_operand(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_difference = subtract_polygons(first, second)
    first_third_union = unite_polygons(first, third)
    second_third_difference = subtract_polygons(second, third)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(first_third_union)
            or not is_polygon(second_third_difference)
            or are_compounds_similar(
                    unite_polygons(first_second_difference, third),
                    subtract_polygons(first_third_union,
                                      second_third_difference)
            ))


@given(strategies.polygons_triplets)
def test_distribution_over_intersection(
        polygons_triplet: PolygonsTriplet
) -> None:
    first, second, third = polygons_triplet

    second_third_intersection = intersect_polygons(second, third)
    first_second_union = unite_polygons(first, second)
    first_third_union = unite_polygons(first, third)
    assert (not is_polygon(second_third_intersection)
            or not is_polygon(first_second_union)
            or not is_polygon(first_third_union)
            or are_compounds_similar(
                    unite_polygons(first, second_third_intersection),
                    intersect_polygons(first_second_union,
                                       first_third_union)
            ))


@given(strategies.polygons_pairs)
def test_equivalents(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = unite_polygons(first, second)

    first_second_symmetric_difference = symmetric_subtract_polygons(first,
                                                                    second)
    first_second_intersection = intersect_polygons(first, second)
    assert (not is_polygon(first_second_symmetric_difference)
            or not is_polygon(first_second_intersection)
            or result == symmetric_subtract_polygons(
                    first_second_symmetric_difference,
                    first_second_intersection
            ))


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = unite_polygons(first, second)

    assert are_compounds_similar(
            result, unite_polygons(first, reverse_polygon_border(second))
    )
    assert are_compounds_similar(
            result, unite_polygons(first, reverse_polygon_holes(second))
    )
    assert are_compounds_similar(
            result, unite_polygons(first,
                                   reverse_polygon_holes_contours(second))
    )
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    unite_polygons(reverse_polygon_coordinates(first),
                                   reverse_polygon_coordinates(second))
            )
    )
