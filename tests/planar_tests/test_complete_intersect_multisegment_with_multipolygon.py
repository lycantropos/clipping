from ground.base import Relation
from hypothesis import given
from orient.planar import (point_in_multipolygon,
                           point_in_multisegment,
                           point_in_segment,
                           segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import (complete_intersect_multisegment_with_multipolygon,
                             intersect_multisegment_with_multipolygon)
from tests.utils import (MultipolygonWithMultisegment,
                         compound_to_linear,
                         contour_to_edges,
                         is_non_shaped,
                         pack_non_shaped,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multisegment,
                         reverse_multisegment_endpoints,
                         segments_relation,
                         to_multipolygon_contours,
                         to_sorted_segment)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment: MultipolygonWithMultisegment
               ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    assert is_non_shaped(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    result_points, result_segments = pack_non_shaped(result)
    assert all(point_in_multisegment(point, multisegment) is Relation.COMPONENT
               for point in result_points)
    assert all(point_in_multipolygon(point, multipolygon) is Relation.COMPONENT
               for point in result_points)
    assert all(any(point_in_segment(point, segment) is Relation.COMPONENT
                   for point in result_points)
               or any(segments_relation(segment, result_segment)
                      is Relation.TOUCH
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   is Relation.TOUCH
                   and all(segments_relation(segment, edge)
                           in (Relation.CROSS, Relation.DISJOINT,
                               Relation.TOUCH)
                           for contour
                           in to_multipolygon_contours(multipolygon)
                           for edge in contour_to_edges(contour))))
    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_multipolygon(segment, multipolygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for segment in result_segments)
    assert all(to_sorted_segment(segment) in result_segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


@given(strategies.multipolygons_with_multisegments)
def test_connection_with_intersect(multipolygon_with_multisegment
                                   : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    assert (compound_to_linear(result)
            == intersect_multisegment_with_multipolygon(multisegment,
                                                        multipolygon))


@given(strategies.multipolygons_with_multisegments)
def test_reversals(multipolygon_with_multisegment: MultipolygonWithMultisegment
                   ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    assert result == complete_intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon(multipolygon))
    assert result == complete_intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_borders(multipolygon))
    assert result == complete_intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_holes(multipolygon))
    assert result == complete_intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_holes_contours(multipolygon))
    assert result == complete_intersect_multisegment_with_multipolygon(
            reverse_multisegment(multisegment), multipolygon)
    assert result == complete_intersect_multisegment_with_multipolygon(
            reverse_multisegment_endpoints(multisegment), multipolygon)
