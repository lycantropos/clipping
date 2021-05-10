from ground.base import Relation
from ground.hints import Multisegment
from hypothesis import given
from orient.planar import (multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import (complete_intersect_multisegments,
                             intersect_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         are_compounds_similar,
                         are_multisegments_equivalent,
                         is_linear_compound,
                         pack_linear_compound,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         segments_intersections,
                         segments_relation,
                         to_sorted_segment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_linear_compound(result)


@given(strategies.multisegments_pairs)
def test_properties(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    result_points, result_segments = pack_linear_compound(result)
    assert all(point_in_multisegment(point, left_multisegment)
               is point_in_multisegment(point, right_multisegment)
               is Relation.COMPONENT
               for point in result_points)
    assert (multisegment_in_multisegment(left_multisegment, right_multisegment)
            is not Relation.TOUCH
            or bool(result_points))
    assert all(all(point in result_points
                   or any(point == segment.start or point == segment.end
                          for segment in result_segments)
                   for right_segment in right_multisegment.segments
                   for point in segments_intersections(left_segment,
                                                       right_segment))
               for left_segment in left_multisegment.segments
               if (segment_in_multisegment(left_segment, right_multisegment)
                   in (Relation.TOUCH, Relation.CROSS)))
    assert all(segment_in_multisegment(segment, left_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_multisegment(segment, right_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(to_sorted_segment(left_segment) in result_segments
               or any(segment_in_segment(segment, left_segment)
                      is Relation.COMPONENT
                      for segment in result_segments)
               for left_segment in left_multisegment.segments
               if any(segments_relation(left_segment, right_segment)
                      not in (Relation.CROSS, Relation.DISJOINT,
                              Relation.TOUCH)
                      for right_segment in right_multisegment.segments))


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = complete_intersect_multisegments(multisegment, multisegment)

    assert are_compounds_similar(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(
            left_multisegment,
            unite_multisegments(left_multisegment, right_multisegment))

    assert are_multisegments_equivalent(result, left_multisegment)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert result == complete_intersect_multisegments(right_multisegment,
                                                      left_multisegment)


@given(strategies.multisegments_pairs)
def test_connection_with_intersect(multisegments_pair: MultisegmentsPair
                                   ) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    _, multisegment = result
    assert multisegment == intersect_multisegments(left_multisegment,
                                                   right_multisegment)


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)
    assert result == complete_intersect_multisegments(
            reverse_multisegment(left_multisegment), right_multisegment)
    assert result == complete_intersect_multisegments(
            left_multisegment, reverse_multisegment(right_multisegment))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
