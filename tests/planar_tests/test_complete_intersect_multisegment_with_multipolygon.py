from ground.base import Relation
from hypothesis import given
from orient.planar import (point_in_multipolygon,
                           point_in_multisegment,
                           point_in_segment,
                           segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.core.utils import contour_to_edges_endpoints
from clipping.planar import (complete_intersect_multisegment_with_multipolygon,
                             intersect_multisegment_with_multipolygon)
from tests.utils import (MultipolygonWithMultisegment,
                         is_linear_mix,
                         is_linear_mix_empty,
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

    assert is_linear_mix(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    result_multipoint, result_multisegment = result
    assert all(point_in_multisegment(point, multisegment) is Relation.COMPONENT
               for point in result_multipoint.points)
    assert all(point_in_multipolygon(point, multipolygon) is Relation.COMPONENT
               for point in result_multipoint.points)
    assert all(any(point_in_segment(point, segment) is Relation.COMPONENT
                   for point in result_multipoint.points)
               or any(segments_relation(segment.start, segment.end,
                                        result_segment.start,
                                        result_segment.end) is Relation.TOUCH
                      for result_segment in result_multisegment.segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   is Relation.TOUCH
                   and all(segments_relation(segment.start, segment.end,
                                             edge_start, edge_end)
                           in (Relation.CROSS, Relation.DISJOINT,
                               Relation.TOUCH)
                           for contour
                           in to_multipolygon_contours(multipolygon)
                           for edge_start, edge_end
                           in contour_to_edges_endpoints(contour))))
    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment.segments)
    assert all(segment_in_multipolygon(segment, multipolygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for segment in result_multisegment.segments)
    assert all(to_sorted_segment(segment) in result_multisegment.segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_multisegment.segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


@given(strategies.empty_multipolygons_with_multisegments)
def test_left_absorbing_element(empty_multipolygon_with_multisegment
                                : MultipolygonWithMultisegment) -> None:
    empty_multipolygon, multisegment = empty_multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(
            multisegment, empty_multipolygon)

    assert is_linear_mix_empty(result)


@given(strategies.multipolygons_with_empty_multisegments)
def test_right_absorbing_element(multipolygon_with_empty_multisegment
                                 : MultipolygonWithMultisegment) -> None:
    multipolygon, empty_multisegment = multipolygon_with_empty_multisegment

    result = complete_intersect_multisegment_with_multipolygon(
            empty_multisegment, multipolygon)

    assert is_linear_mix_empty(result)


@given(strategies.multipolygons_with_multisegments)
def test_connection_with_intersect(multipolygon_with_multisegment
                                   : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = complete_intersect_multisegment_with_multipolygon(multisegment,
                                                               multipolygon)

    _, multisegment = result
    assert multisegment == intersect_multisegment_with_multipolygon(
            multisegment, multipolygon)


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
