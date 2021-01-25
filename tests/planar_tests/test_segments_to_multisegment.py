from typing import List

from bentley_ottmann.planar import segments_cross_or_overlap
from ground.hints import Segment
from hypothesis import given

from clipping.core.linear import segment_to_endpoints
from clipping.planar import segments_to_multisegment
from tests.utils import (equivalence,
                         is_multisegment,
                         to_sorted_segment)
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
                       sorted(result.segments,
                              key=segment_to_endpoints)
                       == sorted(map(to_sorted_segment, segments),
                                 key=segment_to_endpoints))
