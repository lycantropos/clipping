from ground.base import (Location,
                         Relation)
from hypothesis import given
from orient.planar import (point_in_polygon,
                           point_in_segment,
                           segment_in_polygon,
                           segment_in_segment)

from clipping.planar import (complete_intersect_segment_with_polygon,
                             intersect_segment_with_polygon)
from tests.utils import (PolygonWithSegment,
                         are_compounds_similar,
                         compound_to_linear,
                         is_non_shaped,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment,
                         reverse_segment_coordinates,
                         segments_relation,
                         to_contour_segments,
                         to_polygon_contours,
                         to_sorted_segment)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = complete_intersect_segment_with_polygon(segment, polygon)

    assert is_non_shaped(result)


@given(strategies.polygons_with_segments)
def test_properties(polygon_with_segment: PolygonWithSegment
                    ) -> None:
    polygon, segment = polygon_with_segment

    result = complete_intersect_segment_with_polygon(segment, polygon)

    result_points, result_segments = pack_non_shaped(result)
    assert all(point_in_segment(point, segment) is Location.BOUNDARY
               for point in result_points)
    assert all(point_in_polygon(point, polygon) is Location.BOUNDARY
               for point in result_points)
    assert (not (segment_in_polygon(segment, polygon) is Relation.TOUCH
                 and all(segments_relation(segment, contour_segment)
                         in (Relation.CROSS, Relation.DISJOINT, Relation.TOUCH)
                         for contour in to_polygon_contours(polygon)
                         for contour_segment in to_contour_segments(contour)))
            or any(point_in_segment(point, segment) is Location.BOUNDARY
                   for point in result_points)
            or any(segments_relation(segment, result_segment)
                   is Relation.TOUCH
                   for result_segment in result_segments))
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
def test_connection_with_intersect(polygon_with_segment
                                   : PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = complete_intersect_segment_with_polygon(segment, polygon)

    assert (compound_to_linear(result)
            == intersect_segment_with_polygon(segment, polygon))


@given(strategies.polygons_with_segments)
def test_reversals(polygon_with_segment: PolygonWithSegment
                   ) -> None:
    polygon, segment = polygon_with_segment

    result = complete_intersect_segment_with_polygon(segment, polygon)

    assert result == complete_intersect_segment_with_polygon(
            segment, reverse_polygon_border(polygon))
    assert result == complete_intersect_segment_with_polygon(
            segment, reverse_polygon_holes(polygon))
    assert result == complete_intersect_segment_with_polygon(
            segment, reverse_polygon_holes_contours(polygon))
    assert result == complete_intersect_segment_with_polygon(
            reverse_segment(segment), polygon)
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    complete_intersect_segment_with_polygon(
                            reverse_segment_coordinates(segment),
                            reverse_polygon_coordinates(polygon))))
