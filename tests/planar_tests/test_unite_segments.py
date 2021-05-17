from ground.hints import Segment
from hypothesis import given

from clipping.planar import (intersect_segments,
                             subtract_segments,
                             symmetric_subtract_segments,
                             unite_segments)
from tests.utils import (SegmentsPair,
                         SegmentsTriplet,
                         are_compounds_similar,
                         is_homogeneous_non_shaped,
                         is_segment,
                         reverse_compound_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = unite_segments(first, second)

    assert is_homogeneous_non_shaped(result)


@given(strategies.segments)
def test_idempotence(segment: Segment) -> None:
    result = unite_segments(segment, segment)

    assert result == segment


@given(strategies.segments_pairs)
def test_absorption_identity(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    first_second_intersection = intersect_segments(first, second)
    assert (not is_segment(first_second_intersection)
            or unite_segments(first, first_second_intersection) == first)


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = unite_segments(first, second)

    assert are_compounds_similar(result, unite_segments(second, first))


@given(strategies.segments_triplets)
def test_associativity(segments_triplet: SegmentsTriplet) -> None:
    first, second, third = segments_triplet

    first_second_union = unite_segments(first, second)
    second_third_union = unite_segments(second, third)
    assert (not is_segment(first_second_union)
            or not is_segment(second_third_union)
            or are_compounds_similar(unite_segments(first_second_union, third),
                                     unite_segments(first,
                                                    second_third_union)))


@given(strategies.segments_triplets)
def test_difference_operand(segments_triplet: SegmentsTriplet
                            ) -> None:
    first, second, third = segments_triplet

    first_second_difference = subtract_segments(first, second)
    first_third_union = unite_segments(first, third)
    second_third_difference = subtract_segments(second, third)
    assert (not is_segment(first_second_difference)
            or not is_segment(first_third_union)
            or not is_segment(second_third_difference)
            or are_compounds_similar(
                    unite_segments(first_second_difference, third),
                    subtract_segments(first_third_union,
                                      second_third_difference)))


@given(strategies.segments_triplets)
def test_distribution_over_intersection(segments_triplet
                                        : SegmentsTriplet) -> None:
    first, second, third = segments_triplet

    first_second_union = unite_segments(first, second)
    first_third_union = unite_segments(first, third)
    second_third_intersection = intersect_segments(second, third)
    assert (not is_segment(first_second_union)
            or not is_segment(first_third_union)
            or not is_segment(second_third_intersection)
            or are_compounds_similar(
                    unite_segments(first, second_third_intersection),
                    intersect_segments(first_second_union, first_third_union)))


@given(strategies.segments_pairs)
def test_equivalents(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = unite_segments(first, second)

    first_second_symmetric_difference = symmetric_subtract_segments(
            first, second)
    first_second_intersection = intersect_segments(first, second)
    assert (not is_segment(first_second_symmetric_difference)
            or not is_segment(first_second_intersection)
            or are_compounds_similar(result, symmetric_subtract_segments(
                    first_second_symmetric_difference,
                    first_second_intersection)))


@given(strategies.segments_pairs)
def test_reversals(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = unite_segments(first, second)

    assert are_compounds_similar(
            result, unite_segments(first, reverse_segment(second)))
    assert are_compounds_similar(result,
                                 reverse_compound_coordinates(unite_segments(
                                         reverse_segment_coordinates(first),
                                         reverse_segment_coordinates(second))))
