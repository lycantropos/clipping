from ground.base import Relation
from hypothesis import given
from orient.planar import (point_in_multisegment,
                           point_in_polygon,
                           point_in_segment,
                           segment_in_multisegment,
                           segment_in_polygon,
                           segment_in_segment)

from clipping.planar import (complete_intersect_multisegment_with_polygon,
                             intersect_multisegment_with_polygon)
from tests.utils import (PolygonWithMultisegment,
                         compound_to_linear,
                         contour_to_edges,
                         is_non_shaped,
                         pack_non_shaped,
                         reverse_multisegment,
                         reverse_multisegment_endpoints,
                         reverse_polygon_border,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         segments_relation,
                         to_polygon_contours,
                         to_sorted_segment)
from . import strategies


@given(strategies.polygons_with_multisegments)
def test_basic(polygon_with_multisegment: PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = complete_intersect_multisegment_with_polygon(multisegment,
                                                          polygon)

    assert is_non_shaped(result)


@given(strategies.polygons_with_multisegments)
def test_properties(polygon_with_multisegment: PolygonWithMultisegment
                    ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = complete_intersect_multisegment_with_polygon(multisegment,
                                                          polygon)

    result_points, result_segments = pack_non_shaped(result)
    assert all(point_in_multisegment(point, multisegment) is Relation.COMPONENT
               for point in result_points)
    assert all(point_in_polygon(point, polygon) is Relation.COMPONENT
               for point in result_points)
    assert all(any(point_in_segment(point, segment) is Relation.COMPONENT
                   for point in result_points)
               or any(segments_relation(segment, result_segment)
                      is Relation.TOUCH
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_polygon(segment, polygon)
                   is Relation.TOUCH
                   and all(segments_relation(segment, edge)
                           in (Relation.CROSS, Relation.DISJOINT,
                               Relation.TOUCH)
                           for contour in to_polygon_contours(polygon)
                           for edge in contour_to_edges(contour))))
    assert all(segment_in_multisegment(result_segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for result_segment in result_segments)
    assert all(segment_in_polygon(result_segment, polygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for result_segment in result_segments)
    assert all(to_sorted_segment(segment) in result_segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_polygon(segment, polygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


@given(strategies.polygons_with_multisegments)
def test_connection_with_intersect(polygon_with_multisegment
                                   : PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = complete_intersect_multisegment_with_polygon(multisegment,
                                                          polygon)

    assert (compound_to_linear(result)
            == intersect_multisegment_with_polygon(multisegment, polygon))


@given(strategies.polygons_with_multisegments)
def test_reversals(polygon_with_multisegment: PolygonWithMultisegment
                   ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = complete_intersect_multisegment_with_polygon(multisegment,
                                                          polygon)

    assert result == complete_intersect_multisegment_with_polygon(
            multisegment, reverse_polygon_border(polygon))
    assert result == complete_intersect_multisegment_with_polygon(
            multisegment, reverse_polygon_holes(polygon))
    assert result == complete_intersect_multisegment_with_polygon(
            multisegment, reverse_polygon_holes_contours(polygon))
    assert result == complete_intersect_multisegment_with_polygon(
            reverse_multisegment(multisegment), polygon)
    assert result == complete_intersect_multisegment_with_polygon(
            reverse_multisegment_endpoints(multisegment), polygon)
