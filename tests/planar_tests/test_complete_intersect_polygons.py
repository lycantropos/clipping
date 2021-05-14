from ground.hints import Polygon
from hypothesis import given

from clipping.planar import (complete_intersect_polygons,
                             intersect_polygons,
                             unite_polygons)
from tests.utils import (PolygonsPair,
                         are_compounds_similar,
                         compound_to_shaped,
                         is_compound,
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

    result = complete_intersect_polygons(first, second)

    assert is_compound(result)


@given(strategies.polygons)
def test_idempotence(polygon: Polygon) -> None:
    result = complete_intersect_polygons(polygon, polygon)

    assert are_compounds_similar(result, polygon)


@given(strategies.polygons_pairs)
def test_absorption_identity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    first_second_union = unite_polygons(first, second)

    assert (not is_polygon(first_second_union)
            or are_compounds_similar(
                    first,
                    complete_intersect_polygons(first_second_union,
                                                     first)))


@given(strategies.polygons_pairs)
def test_commutativity(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = complete_intersect_polygons(first, second)

    assert result == complete_intersect_polygons(second, first)


@given(strategies.polygons_pairs)
def test_connection_with_intersect(polygons_pair: PolygonsPair
                                   ) -> None:
    first, second = polygons_pair

    result = complete_intersect_polygons(first, second)

    assert compound_to_shaped(result) == intersect_polygons(first, second)


@given(strategies.polygons_pairs)
def test_reversals(polygons_pair: PolygonsPair) -> None:
    first, second = polygons_pair

    result = complete_intersect_polygons(first, second)

    assert result == complete_intersect_polygons(
            first, reverse_polygon_border(second))
    assert result == complete_intersect_polygons(
            first, reverse_polygon_holes(second))
    assert result == complete_intersect_polygons(
            first, reverse_polygon_holes_contours(second))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_polygons(
                    reverse_polygon_coordinates(first),
                    reverse_polygon_coordinates(second))))
