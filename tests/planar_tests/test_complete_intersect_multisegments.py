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
                         compound_to_linear,
                         is_non_shaped,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         segments_intersections,
                         segments_relation,
                         to_sorted_segment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = complete_intersect_multisegments(first, second)

    assert is_non_shaped(result)


@given(strategies.multisegments_pairs)
def test_properties(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = complete_intersect_multisegments(first, second)

    result_points, result_segments = pack_non_shaped(result)
    assert all(point_in_multisegment(point, first)
               is point_in_multisegment(point, second) is Relation.COMPONENT
               for point in result_points)
    assert (multisegment_in_multisegment(first, second) is not Relation.TOUCH
            or bool(result_points))
    assert all(all(point in result_points
                   or any(point == result_segment.start
                          or point == result_segment.end
                          for result_segment in result_segments)
                   for second_segment in second.segments
                   for point in segments_intersections(first_segment,
                                                       second_segment))
               for first_segment in first.segments
               if (segment_in_multisegment(first_segment, second)
                   in (Relation.TOUCH, Relation.CROSS)))
    assert all(segment_in_multisegment(result_segment, first)
               in (Relation.EQUAL, Relation.COMPONENT)
               for result_segment in result_segments)
    assert all(segment_in_multisegment(result_segment, second)
               in (Relation.EQUAL, Relation.COMPONENT)
               for result_segment in result_segments)
    assert all(to_sorted_segment(first_segment) in result_segments
               or any(segment_in_segment(result_segment, first_segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for first_segment in first.segments
               if any(segments_relation(first_segment, second_segment)
                      not in (Relation.CROSS, Relation.DISJOINT,
                              Relation.TOUCH)
                      for second_segment in second.segments))


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = complete_intersect_multisegments(multisegment, multisegment)

    assert are_compounds_similar(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    assert are_multisegments_equivalent(
            complete_intersect_multisegments(first,
                                             unite_multisegments(first,
                                                                 second)),
            first)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = complete_intersect_multisegments(first, second)

    assert result == complete_intersect_multisegments(second, first)


@given(strategies.multisegments_pairs)
def test_connection_with_intersect(multisegments_pair: MultisegmentsPair
                                   ) -> None:
    first, second = multisegments_pair

    result = complete_intersect_multisegments(first, second)

    assert compound_to_linear(result) == intersect_multisegments(first, second)


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = complete_intersect_multisegments(first,
                                              second)
    assert result == complete_intersect_multisegments(
            first, reverse_multisegment(second))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(complete_intersect_multisegments(
                    reverse_multisegment_coordinates(first),
                    reverse_multisegment_coordinates(second))))
