from typing import List

from bentley_ottmann.planar import segments_cross_or_overlap
from hypothesis import given

from clipping.hints import Segment
from clipping.planar import segments_to_multisegment
from tests.utils import (equivalence,
                         is_multisegment,
                         sort_pair)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert is_multisegment(result)


@given(strategies.rational_segments_lists)
def test_properties(segments: List[Segment]) -> None:
    result = segments_to_multisegment(segments)

    assert not segments_cross_or_overlap(result)
    assert equivalence(not segments_cross_or_overlap(segments),
                       result == sorted(map(sort_pair, segments)))
