from ground.base import Relation
from hypothesis import given
from orient.planar import (segment_in_polygon,
                           segment_in_segment)

from clipping.planar import intersect_segment_with_polygon
from tests.utils import (PolygonWithSegment,
                         are_compounds_similar,
                         is_maybe_linear,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment,
                         reverse_segment_coordinates,
                         to_sorted_segment)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = intersect_segment_with_polygon(segment, polygon)

    assert is_maybe_linear(result)


@given(strategies.polygons_with_segments)
def test_properties(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = intersect_segment_with_polygon(segment, polygon)

    result_points, result_segments = pack_non_shaped(result)
    assert not result_points
    assert all(segment_in_segment(result_segment, segment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for result_segment in result_segments)
    assert all(segment_in_polygon(result_segment, polygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for result_segment in result_segments)
    assert (segment_in_polygon(segment, polygon)
            not in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                    Relation.WITHIN)
            or to_sorted_segment(segment) in result_segments
            # in case of cross
            or any(segment_in_segment(result_segment, segment)
                   is Relation.COMPONENT
                   for result_segment in result_segments))


@given(strategies.polygons_with_segments)
def test_reversals(polygon_with_segment: PolygonWithSegment
                   ) -> None:
    polygon, segment = polygon_with_segment

    result = intersect_segment_with_polygon(segment, polygon)

    assert result == intersect_segment_with_polygon(
            segment, reverse_polygon_border(polygon))
    assert result == intersect_segment_with_polygon(
            segment, reverse_polygon_holes(polygon))
    assert result == intersect_segment_with_polygon(
            segment, reverse_polygon_holes_contours(polygon))
    assert result == intersect_segment_with_polygon(
            reverse_segment(segment), polygon)
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    intersect_segment_with_polygon(
                            reverse_segment_coordinates(segment),
                            reverse_polygon_coordinates(polygon))))
