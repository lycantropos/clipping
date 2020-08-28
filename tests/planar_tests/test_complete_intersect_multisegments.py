from hypothesis import given
from orient.planar import (Relation,
                           multisegment_in_multisegment,
                           point_in_multisegment,
                           segment_in_multisegment,
                           segment_in_segment)
from robust.linear import (SegmentsRelationship,
                           segments_intersections,
                           segments_relationship)

from clipping.hints import Multisegment
from clipping.planar import (complete_intersect_multisegments,
                             intersect_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         is_mix,
                         mix_equivalent_to_multisegment,
                         reverse_multisegment,
                         sort_pair)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_mix(result)


@given(strategies.rational_multisegments_pairs)
def test_properties(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    result_multipoint, result_multisegment, result_multipolygon = result
    assert all(point_in_multisegment(point, left_multisegment)
               is point_in_multisegment(point, right_multisegment)
               is Relation.COMPONENT
               for point in result_multipoint)
    assert (multisegment_in_multisegment(left_multisegment, right_multisegment)
            is not Relation.TOUCH
            or bool(result_multipoint))
    assert all(all(point in result_multipoint
                   or any(point in segment
                          for segment in result_multisegment)
                   for right_segment in right_multisegment
                   for point in segments_intersections(left_segment,
                                                       right_segment))
               for left_segment in left_multisegment
               if (segment_in_multisegment(left_segment, right_multisegment)
                   in (Relation.TOUCH, Relation.CROSS)))
    assert all(segment_in_multisegment(segment, left_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment)
    assert all(segment_in_multisegment(segment, right_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment)
    assert all(sort_pair(left_segment) in result_multisegment
               or any(segment_in_segment(segment, left_segment)
                      is Relation.COMPONENT
                      for segment in result_multisegment)
               for left_segment in left_multisegment
               if any(segments_relationship(left_segment, right_segment)
                      is SegmentsRelationship.OVERLAP
                      for right_segment in right_multisegment))
    assert not result_multipolygon


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = complete_intersect_multisegments(multisegment, multisegment)

    assert mix_equivalent_to_multisegment(result, multisegment)


@given(strategies.empty_multisegments_with_multisegments)
def test_left_absorbing_element(empty_multisegment_with_multisegment
                                : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(empty_multisegment, multisegment)

    assert not any(result)


@given(strategies.empty_multisegments_with_multisegments)
def test_right_absorbing_element(empty_multisegment_with_multisegment
                                 : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(multisegment, empty_multisegment)

    assert not any(result)


@given(strategies.rational_multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(
            left_multisegment,
            unite_multisegments(left_multisegment, right_multisegment))

    assert mix_equivalent_to_multisegment(result, left_multisegment)


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

    _, multisegment, _ = result
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
