from typing import List

from bentley_ottmann.planar import segments_cross_or_overlap
from ground.hints import Segment
from hypothesis import given

from clipping.planar import segments_to_multisegment
from tests.utils import (are_multisegments_similar,
                         are_segments_sequences_similar,
                         equivalence,
                         is_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_segments_sequence,
                         reverse_segments_sequence_coordinates,
                         reverse_segments_sequence_endpoints)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert is_multisegment(result)


@given(strategies.segments_lists)
def test_properties(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert not segments_cross_or_overlap(result.segments)
    assert equivalence(not segments_cross_or_overlap(segments),
                       are_segments_sequences_similar(result.segments,
                                                      segments))


@given(strategies.segments_lists)
def test_reversals(segments: List[Segment]) -> None:
    segments = segments

    result = segments_to_multisegment(segments)

    assert result == segments_to_multisegment(
            reverse_segments_sequence(segments))
    assert result == segments_to_multisegment(
            reverse_segments_sequence_endpoints(segments))
    assert are_multisegments_similar(
            result, reverse_multisegment_coordinates(segments_to_multisegment(
                    reverse_segments_sequence_coordinates(segments))))
