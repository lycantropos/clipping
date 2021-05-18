from hypothesis import given

from clipping.planar import intersect_segment_with_multisegment
from tests.utils import (MultisegmentWithSegment,
                         are_compounds_similar,
                         is_non_shaped,
                         is_non_shaped_valid,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_multisegment_endpoints,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.multisegments_with_segments)
def test_basic(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = intersect_segment_with_multisegment(segment, multisegment)

    assert is_non_shaped(result)


@given(strategies.multisegments_with_segments)
def test_validity(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = intersect_segment_with_multisegment(segment, multisegment)

    assert is_non_shaped_valid(result)


@given(strategies.multisegments_with_segments)
def test_reversals(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = intersect_segment_with_multisegment(segment, multisegment)

    assert are_compounds_similar(
            result, intersect_segment_with_multisegment(
                    segment, reverse_multisegment(multisegment)))
    assert are_compounds_similar(
            result, intersect_segment_with_multisegment(
                    segment, reverse_multisegment_endpoints(multisegment)))
    assert are_compounds_similar(
            result,
            intersect_segment_with_multisegment(reverse_segment(segment),
                                                multisegment))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    intersect_segment_with_multisegment(
                            reverse_segment_coordinates(segment),
                            reverse_multisegment_coordinates(multisegment))))
