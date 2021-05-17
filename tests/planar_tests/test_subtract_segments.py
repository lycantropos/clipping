from hypothesis import given

from clipping.planar import (intersect_segments,
                             subtract_segments,
                             unite_segments)
from tests.utils import (SegmentsPair,
                         SegmentsTriplet,
                         are_compounds_similar,
                         equivalence,
                         is_maybe_linear,
                         is_segment,
                         reverse_compound_coordinates,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = subtract_segments(first, second)

    assert is_maybe_linear(result)


@given(strategies.segments_pairs)
def test_commutative_case(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = subtract_segments(first, second)

    assert equivalence(result == subtract_segments(second, first),
                       first == second)


@given(strategies.segments_triplets)
def test_difference_subtrahend(segments_triplet: SegmentsTriplet
                               ) -> None:
    first, second, third = segments_triplet

    first_second_difference = subtract_segments(first, second)
    first_third_difference = intersect_segments(first, third)
    second_third_difference = subtract_segments(second, third)
    assert (not is_segment(first_second_difference)
            or not is_segment(first_third_difference)
            or not is_segment(second_third_difference)
            or are_compounds_similar(
                    subtract_segments(first, second_third_difference),
                    unite_segments(first_second_difference,
                                   first_third_difference)))


@given(strategies.segments_triplets)
def test_intersection_minuend(segments_triplet: SegmentsTriplet
                              ) -> None:
    first, second, third = segments_triplet

    first_second_intersection = intersect_segments(first, second)
    second_third_difference = subtract_segments(second, third)
    assert (not is_segment(first_second_intersection)
            or not is_segment(second_third_difference)
            or are_compounds_similar(
                    subtract_segments(first_second_intersection, third),
                    intersect_segments(first, second_third_difference)))


@given(strategies.segments_triplets)
def test_intersection_subtrahend(segments_triplet: SegmentsTriplet
                                 ) -> None:
    first, second, third = segments_triplet

    first_second_difference = subtract_segments(first, second)
    first_third_difference = subtract_segments(first, third)
    second_third_intersection = intersect_segments(second, third)
    assert (not is_segment(first_second_difference)
            or not is_segment(first_third_difference)
            or not is_segment(second_third_intersection)
            or are_compounds_similar(
                    subtract_segments(first, second_third_intersection),
                    unite_segments(first_second_difference,
                                   first_third_difference)))


@given(strategies.segments_triplets)
def test_union_subtrahend(segments_triplet: SegmentsTriplet) -> None:
    first, second, third = segments_triplet

    first_second_difference = subtract_segments(first, second)
    first_third_difference = subtract_segments(first, third)
    second_third_union = unite_segments(second, third)
    assert (not is_segment(first_second_difference)
            or not is_segment(first_third_difference)
            or not is_segment(second_third_union)
            or are_compounds_similar(
                    subtract_segments(first, second_third_union),
                    intersect_segments(first_second_difference,
                                       first_third_difference)))


@given(strategies.segments_pairs)
def test_reversals(segments_pair: SegmentsPair) -> None:
    first, second = segments_pair

    result = subtract_segments(first, second)

    assert are_compounds_similar(result,
                                 subtract_segments(reverse_segment(first),
                                                   second))
    assert result == subtract_segments(first, reverse_segment(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_segments(
                    reverse_segment_coordinates(first),
                    reverse_segment_coordinates(second))))
