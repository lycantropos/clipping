from typing import List

from bentley_ottmann.planar import segments_cross_or_overlap
from ground.hints import Segment
from hypothesis import given

from clipping.planar import segments_to_multisegment
from tests.utils import (are_compounds_similar,
                         are_segments_sequences_similar,
                         equivalence,
                         is_maybe_linear,
                         is_multisegment,
                         is_multisegment_valid,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_segments_sequence,
                         reverse_segments_sequence_coordinates,
                         reverse_segments_sequence_endpoints)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert is_maybe_linear(result)


@given(strategies.segments_lists)
def test_validity(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert not is_multisegment(result) or is_multisegment_valid(result)


@given(strategies.segments_lists)
def test_properties(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    result_points, result_segments = pack_non_shaped(result)
    assert not result_points
    assert equivalence(not segments_cross_or_overlap(segments),
                       are_segments_sequences_similar(result_segments,
                                                      segments))


@given(strategies.segments_lists)
def test_reversals(segments: List[Segment]) -> None:
    segments = segments

    result = segments_to_multisegment(segments)

    assert result == segments_to_multisegment(
            reverse_segments_sequence(segments))
    assert result == segments_to_multisegment(
            reverse_segments_sequence_endpoints(segments))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(segments_to_multisegment(
                    reverse_segments_sequence_coordinates(segments))))
