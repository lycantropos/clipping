from ground.hints import Multisegment
from hypothesis import given
from orient.planar import (Relation,
                           multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import (complete_intersect_multisegments,
                             intersect_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         is_linear_mix,
                         is_linear_mix_empty,
                         linear_mix_equivalent_to_multisegment,
                         reverse_multisegment,
                         segments_intersections,
                         segments_relation,
                         to_sorted_segment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_linear_mix(result)


@given(strategies.multisegments_pairs)
def test_properties(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    result_multipoint, result_multisegment = result
    assert all(point_in_multisegment(point, left_multisegment)
               is point_in_multisegment(point, right_multisegment)
               is Relation.COMPONENT
               for point in result_multipoint.points)
    assert (multisegment_in_multisegment(left_multisegment, right_multisegment)
            is not Relation.TOUCH
            or bool(result_multipoint.points))
    assert all(all(point in result_multipoint.points
                   or any(point == segment.start or point == segment.end
                          for segment in result_multisegment.segments)
                   for right_segment in right_multisegment.segments
                   for point in segments_intersections(left_segment,
                                                       right_segment))
               for left_segment in left_multisegment.segments
               if (segment_in_multisegment(left_segment, right_multisegment)
                   in (Relation.TOUCH, Relation.CROSS)))
    assert all(segment_in_multisegment(segment, left_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment.segments)
    assert all(segment_in_multisegment(segment, right_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment.segments)
    assert all(to_sorted_segment(left_segment) in result_multisegment.segments
               or any(segment_in_segment(segment, left_segment)
                      is Relation.COMPONENT
                      for segment in result_multisegment.segments)
               for left_segment in left_multisegment.segments
               if any(segments_relation(left_segment.start, left_segment.end,
                                        right_segment.start, right_segment.end)
                      not in (Relation.CROSS, Relation.DISJOINT,
                              Relation.TOUCH)
                      for right_segment in right_multisegment.segments))


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = complete_intersect_multisegments(multisegment, multisegment)

    assert linear_mix_equivalent_to_multisegment(result, multisegment)


@given(strategies.empty_multisegments_with_multisegments)
def test_left_absorbing_element(empty_multisegment_with_multisegment
                                : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(empty_multisegment, multisegment)

    assert is_linear_mix_empty(result)


@given(strategies.empty_multisegments_with_multisegments)
def test_right_absorbing_element(empty_multisegment_with_multisegment
                                 : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(multisegment, empty_multisegment)

    assert is_linear_mix_empty(result)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(
            left_multisegment,
            unite_multisegments(left_multisegment, right_multisegment))

    assert linear_mix_equivalent_to_multisegment(result, left_multisegment)


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
