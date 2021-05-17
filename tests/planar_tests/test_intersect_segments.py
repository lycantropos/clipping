from ground.base import Relation
from ground.hints import Segment
from hypothesis import given
from orient.planar import (point_in_segment,
                           segment_in_segment)

from clipping.planar import (intersect_segments,
                             unite_segments)
from tests.utils import (SegmentsPair,
                         are_compounds_similar,
                         is_homogeneous_non_shaped,
                         is_segment, pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates,
                         segments_intersections,
                         segments_relation,
                         to_sorted_segment)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = intersect_segments(first, second)

    assert is_homogeneous_non_shaped(result)


@given(strategies.segments_pairs)
def test_properties(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = intersect_segments(first, second)

    result_points, result_segments = pack_non_shaped(result)
    assert all(point_in_segment(point, first)
               is point_in_segment(point, second) is Relation.COMPONENT
               for point in result_points)
    assert (segment_in_segment(first, second) is not Relation.TOUCH
            or bool(result_points))
    assert (segment_in_segment(first, second) not in (Relation.TOUCH,
                                                      Relation.CROSS)
            or all(point in result_points
                   or any(point == segment.start or point == segment.end
                          for segment in result_segments)
                   for point in segments_intersections(first, second)))
    assert all(segment_in_segment(segment, first)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_segment(segment, second)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert (segments_relation(first, second) in (Relation.CROSS,
                                                 Relation.DISJOINT,
                                                 Relation.TOUCH)
            or to_sorted_segment(first) in result_segments
            or any(segment_in_segment(segment, first) is Relation.COMPONENT
                   for segment in result_segments))


@given(strategies.segments)
def test_idempotence(segment: Segment) -> None:
    result = intersect_segments(segment, segment)

    assert result == segment


@given(strategies.segments_pairs)
def test_absorption_identity(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    first_second_union = unite_segments(first, second)
    assert (not is_segment(first_second_union)
            or intersect_segments(first, first_second_union) == first)


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = intersect_segments(first, second)

    assert are_compounds_similar(result, intersect_segments(second, first))


@given(strategies.segments_pairs)
def test_reversals(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = intersect_segments(first, second)
    assert result == intersect_segments(first, reverse_segment(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(intersect_segments(
                    reverse_segment_coordinates(first),
                    reverse_segment_coordinates(second))))
