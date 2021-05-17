from hypothesis import given

from clipping.planar import (intersect_segments,
                             subtract_segments,
                             symmetric_subtract_segments,
                             unite_segments)
from tests.utils import (Segment,
                         SegmentsPair,
                         SegmentsTriplet,
                         are_compounds_similar,
                         is_empty,
                         is_maybe_linear,
                         is_segment,
                         reverse_compound_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = symmetric_subtract_segments(first, second)

    assert is_maybe_linear(result)


@given(strategies.segments)
def test_self_inverse(segment: Segment) -> None:
    result = symmetric_subtract_segments(segment, segment)

    assert is_empty(result)


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = symmetric_subtract_segments(first, second)

    assert are_compounds_similar(result,
                                 symmetric_subtract_segments(second, first))


@given(strategies.segments_triplets)
def test_associativity(segments_triplet: SegmentsTriplet) -> None:
    first, second, third = segments_triplet

    first_second_symmetric_difference = symmetric_subtract_segments(first,
                                                                    second)
    second_third_symmetric_difference = symmetric_subtract_segments(second,
                                                                    third)
    assert (not is_segment(first_second_symmetric_difference)
            or not is_segment(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_segments(
                            first_second_symmetric_difference, third),
                    symmetric_subtract_segments(
                            first, second_third_symmetric_difference)))


@given(strategies.segments_triplets)
def test_repeated(segments_triplet: SegmentsTriplet) -> None:
    first, second, third = segments_triplet

    first_second_symmetric_difference = symmetric_subtract_segments(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_segments(
            second, third)
    assert (not is_segment(first_second_symmetric_difference)
            or not is_segment(second_third_symmetric_difference)
            or are_compounds_similar(
                    symmetric_subtract_segments(
                            first_second_symmetric_difference,
                            second_third_symmetric_difference),
                    symmetric_subtract_segments(first, third)))


@given(strategies.segments_pairs)
def test_equivalents(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = symmetric_subtract_segments(first, second)

    first_second_difference = subtract_segments(first, second)
    first_second_union = unite_segments(first, second)
    second_first_difference = subtract_segments(second, first)
    second_first_intersection = intersect_segments(second, first)
    assert (not is_segment(second_first_intersection)
            or not is_segment(first_second_union)
            or are_compounds_similar(
                    result, subtract_segments(first_second_union,
                                              second_first_intersection)))
    assert (not is_segment(first_second_difference)
            or not is_segment(second_first_difference)
            or are_compounds_similar(result,
                                     unite_segments(first_second_difference,
                                                    second_first_difference)))


@given(strategies.segments_pairs)
def test_reversals(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = symmetric_subtract_segments(first, second)

    assert are_compounds_similar(
            result, symmetric_subtract_segments(first,
                                                reverse_segment(second)))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(symmetric_subtract_segments(
                    reverse_segment_coordinates(first),
                    reverse_segment_coordinates(second))))
