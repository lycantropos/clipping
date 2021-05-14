from ground.hints import Polygon
from hypothesis import given

from clipping.planar import (intersect_polygons,
                             subtract_polygons,
                             unite_polygons)
from tests.utils import (PolygonsPair,
                         PolygonsTriplet,
                         are_compounds_similar,
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

    result = intersect_polygons(first, second)

    assert is_maybe_shaped(result)


@given(strategies.polygons)
def test_idempotence(polygon: Polygon) -> None:
    result = intersect_polygons(polygon, polygon)

    assert are_compounds_similar(result, polygon)


@given(strategies.polygons_pairs)
def test_absorption_identity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    first_second_union = unite_polygons(first, second)
    assert (not is_polygon(first_second_union)
            or are_compounds_similar(
                    intersect_polygons(first_second_union, first), first))


@given(strategies.polygons_pairs)
def test_commutativity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = intersect_polygons(first, second)

    assert result == intersect_polygons(second, first)


@given(strategies.polygons_triplets)
def test_associativity(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_intersection = intersect_polygons(first, second)
    second_third_intersection = intersect_polygons(second, third)
    assert (not is_polygon(first_second_intersection)
            or not is_polygon(second_third_intersection)
            or (intersect_polygons(first_second_intersection, third)
                == intersect_polygons(first, second_third_intersection)))


@given(strategies.polygons_triplets)
def test_difference_operand(polygons_triplet: PolygonsTriplet
                            ) -> None:
    first, second, third = polygons_triplet

    first_second_difference = subtract_polygons(first, second)
    first_third_intersection = intersect_polygons(first, third)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(first_third_intersection)
            or (intersect_polygons(first_second_difference, third)
                == subtract_polygons(first_third_intersection, second)))


@given(strategies.polygons_triplets)
def test_distribution_over_union(polygons_triplet: PolygonsTriplet
                                 ) -> None:
    first, second, third = polygons_triplet

    second_third_union = unite_polygons(second, third)
    first_second_intersection = intersect_polygons(first, second)
    first_third_intersection = intersect_polygons(first, third)
    assert (not is_polygon(second_third_union)
            or not is_polygon(first_second_intersection)
            or not is_polygon(first_third_intersection)
            or (intersect_polygons(first, second_third_union)
                == unite_polygons(first_second_intersection,
                                  first_third_intersection)))


@given(strategies.polygons_pairs)
def test_equivalents(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = intersect_polygons(first, second)

    first_second_difference = subtract_polygons(first, second)
    assert (not is_polygon(first_second_difference)
            or are_compounds_similar(result,
                                     subtract_polygons(
                                             first, first_second_difference)))


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = intersect_polygons(first, second)

    assert result == intersect_polygons(first, reverse_polygon_border(second))
    assert result == intersect_polygons(first, reverse_polygon_holes(second))
    assert result == intersect_polygons(first,
                                        reverse_polygon_holes_contours(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(intersect_polygons(
                    reverse_polygon_coordinates(first),
                    reverse_polygon_coordinates(second))))
