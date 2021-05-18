from bentley_ottmann.planar import segments_cross_or_overlap
from ground.base import Relation
from hypothesis import given
from orient.planar import segment_in_multisegment

from clipping.planar import unite_segment_with_multisegment
from tests.utils import (MultisegmentWithSegment,
                         are_compounds_similar,
                         is_linear,
                         is_multisegment,
                         is_segment, reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_multisegment_endpoints,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.multisegments_with_segments)
def test_basic(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = unite_segment_with_multisegment(segment, multisegment)

    assert is_linear(result)


@given(strategies.multisegments_with_segments)
def test_validity(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = unite_segment_with_multisegment(segment, multisegment)

    assert (not is_multisegment(result)
            or not segments_cross_or_overlap(result.segments))


@given(strategies.multisegments_with_segments)
def test_properties(multisegment_with_segment: MultisegmentWithSegment
                    ) -> None:
    multisegment, segment = multisegment_with_segment

    result = unite_segment_with_multisegment(segment, multisegment)

    relation = segment_in_multisegment(segment, multisegment)
    assert (not is_multisegment(result)
            or relation in (Relation.DISJOINT, Relation.TOUCH, Relation.CROSS,
                            Relation.OVERLAP, Relation.COMPONENT))
    assert (not is_segment(result) or relation is Relation.EQUAL
            or relation is Relation.COMPOSITE)


@given(strategies.multisegments_with_segments)
def test_reversals(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = unite_segment_with_multisegment(segment, multisegment)

    assert are_compounds_similar(
            result, unite_segment_with_multisegment(
                    segment, reverse_multisegment(multisegment)))
    assert are_compounds_similar(
            result, unite_segment_with_multisegment(
                    segment, reverse_multisegment_endpoints(multisegment)))
    assert are_compounds_similar(
            result, unite_segment_with_multisegment(reverse_segment(segment),
                                                    multisegment))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    unite_segment_with_multisegment(
                            reverse_segment_coordinates(segment),
                            reverse_multisegment_coordinates(multisegment))))
