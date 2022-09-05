from hypothesis import given

from clipping.planar import (intersect_polygons,
                             subtract_polygons,
                             unite_polygons)
from tests.utils import (PolygonsPair,
                         PolygonsTriplet,
                         are_compounds_similar,
                         equivalence,
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

    result = subtract_polygons(first, second)

    assert is_maybe_shaped(result)


@given(strategies.polygons_pairs)
def test_commutative_case(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = subtract_polygons(first, second)

    assert equivalence(result == subtract_polygons(second, first),
                       are_compounds_similar(first, second))


@given(strategies.polygons_triplets)
def test_difference_subtrahend(polygons_triplet: PolygonsTriplet
                               ) -> None:
    first, second, third = polygons_triplet

    first_third_intersection = intersect_polygons(first, third)
    first_second_difference = subtract_polygons(first, second)
    second_third_difference = subtract_polygons(second, third)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(first_third_intersection)
            or not is_polygon(second_third_difference)
            or are_compounds_similar(
                    subtract_polygons(first, second_third_difference),
                    unite_polygons(first_second_difference,
                                   first_third_intersection)
            ))


@given(strategies.polygons_triplets)
def test_intersection_minuend(polygons_triplet: PolygonsTriplet
                              ) -> None:
    first, second, third = polygons_triplet

    first_second_intersection = intersect_polygons(first, second)
    second_third_difference = subtract_polygons(second, third)
    assert (not is_polygon(first_second_intersection)
            or not is_polygon(second_third_difference)
            or (subtract_polygons(first_second_intersection, third)
                == intersect_polygons(first, second_third_difference)))


@given(strategies.polygons_triplets)
def test_intersection_subtrahend(polygons_triplet: PolygonsTriplet
                                 ) -> None:
    first, second, third = polygons_triplet

    first_second_difference = subtract_polygons(first, second)
    first_third_difference = subtract_polygons(first, third)
    second_third_intersection = intersect_polygons(second, third)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(first_third_difference)
            or not is_polygon(second_third_intersection)
            or are_compounds_similar(
                    subtract_polygons(first, second_third_intersection),
                    unite_polygons(first_second_difference,
                                   first_third_difference)))


@given(strategies.polygons_triplets)
def test_union_subtrahend(polygons_triplet: PolygonsTriplet) -> None:
    first, second, third = polygons_triplet

    first_second_difference = subtract_polygons(first, second)
    first_third_difference = subtract_polygons(first, third)
    second_third_union = unite_polygons(second, third)
    assert (not is_polygon(first_second_difference)
            or not is_polygon(first_third_difference)
            or not is_polygon(second_third_union)
            or are_compounds_similar(
                    subtract_polygons(first, second_third_union),
                    intersect_polygons(first_second_difference,
                                       first_third_difference)
            ))


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = subtract_polygons(first, second)

    assert are_compounds_similar(
            result, subtract_polygons(reverse_polygon_border(first), second))
    assert result == subtract_polygons(first, reverse_polygon_border(second))
    assert are_compounds_similar(
            result, subtract_polygons(reverse_polygon_holes(first), second)
    )
    assert result == subtract_polygons(first, reverse_polygon_holes(second))
    assert are_compounds_similar(
            result,
            subtract_polygons(reverse_polygon_holes_contours(first), second))
    assert result == subtract_polygons(first,
                                       reverse_polygon_holes_contours(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_polygons(
                    reverse_polygon_coordinates(first),
                    reverse_polygon_coordinates(second))))
