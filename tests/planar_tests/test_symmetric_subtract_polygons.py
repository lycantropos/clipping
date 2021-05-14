from ground.hints import Polygon
from hypothesis import given

from clipping.planar import (intersect_polygons,
                             subtract_polygons,
                             symmetric_subtract_polygons,
                             unite_polygons)
from tests.utils import (PolygonsPair,
                         PolygonsTriplet,
                         are_compounds_similar,
                         is_empty,
                         is_maybe_shaped,
                         is_polygon,
                         reverse_compound_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours)
from . import strategies


@given(strategies.polygons_pairs)
def test_basic(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = symmetric_subtract_polygons(first, second)

    assert is_maybe_shaped(result)


@given(strategies.polygons)
def test_self_inverse(polygon: Polygon) -> None:
    result = symmetric_subtract_polygons(polygon, polygon)

    assert is_empty(result)


@given(strategies.polygons_pairs)
def test_commutativity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = symmetric_subtract_polygons(first, second)

    assert result == symmetric_subtract_polygons(second, first)


@given(strategies.polygons_triplets)
def test_associativity(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_symmetric_difference = symmetric_subtract_polygons(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_polygons(
            second, third)
    assert (not is_polygon(first_second_symmetric_difference)
            or not is_polygon(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_polygons(
                            first_second_symmetric_difference, third),
                    symmetric_subtract_polygons(
                            first,
                            second_third_symmetric_difference)))


@given(strategies.polygons_triplets)
def test_repeated(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_symmetric_difference = symmetric_subtract_polygons(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_polygons(
            second, third)
    assert (not is_polygon(first_second_symmetric_difference)
            or not is_polygon(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_polygons(
                            first_second_symmetric_difference,
                            second_third_symmetric_difference),
                    symmetric_subtract_polygons(first,
                                                     third)))


@given(strategies.polygons_pairs)
def test_equivalents(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = symmetric_subtract_polygons(first, second)

    first_second_difference = subtract_polygons(first, second)
    first_second_union = unite_polygons(first, second)
    second_first_difference = subtract_polygons(second, first)
    second_first_intersection = intersect_polygons(second, first)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(second_first_difference)
            or result == unite_polygons(first_second_difference,
                                             second_first_difference))
    assert (not is_polygon(first_second_union)
            or not is_polygon(second_first_intersection)
            or result == subtract_polygons(first_second_union,
                                                second_first_intersection))


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = symmetric_subtract_polygons(first, second)

    assert are_compounds_similar(
            result, symmetric_subtract_polygons(
                    first, reverse_polygon_border(second)))
    assert are_compounds_similar(
            result, symmetric_subtract_polygons(
                    first, reverse_polygon_holes(second)))
    assert are_compounds_similar(
            result, symmetric_subtract_polygons(
                    first, reverse_polygon_holes_contours(second)))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(symmetric_subtract_polygons(
                    reverse_polygon_coordinates(first),
                    reverse_polygon_coordinates(second))))
