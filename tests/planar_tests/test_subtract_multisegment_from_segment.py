from ground.base import Relation
from hypothesis import given
from orient.planar import segment_in_multisegment

from clipping.planar import subtract_multisegment_from_segment
from tests.utils import (MultisegmentWithSegment,
                         are_compounds_similar,
                         equivalence,
                         implication,
                         is_empty,
                         is_maybe_linear,
                         is_multisegment,
                         is_multisegment_valid,
                         is_segment,
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

    result = subtract_multisegment_from_segment(segment, multisegment)

    assert is_maybe_linear(result)


@given(strategies.multisegments_with_segments)
def test_validity(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = subtract_multisegment_from_segment(segment, multisegment)

    assert not is_multisegment(result) or is_multisegment_valid(result)


@given(strategies.multisegments_with_segments)
def test_properties(multisegment_with_segment: MultisegmentWithSegment
                    ) -> None:
    multisegment, segment = multisegment_with_segment

    result = subtract_multisegment_from_segment(segment, multisegment)

    relation = segment_in_multisegment(segment, multisegment)
    assert equivalence(is_empty(result),
                       relation is Relation.EQUAL
                       or relation is Relation.COMPONENT)
    assert implication(is_multisegment(result),
                       relation in (Relation.TOUCH, Relation.CROSS,
                                    Relation.COMPOSITE, Relation.OVERLAP))
    assert implication(is_segment(result),
                       relation in (Relation.DISJOINT, Relation.TOUCH,
                                    Relation.CROSS, Relation.COMPOSITE,
                                    Relation.OVERLAP))


@given(strategies.multisegments_with_segments)
def test_reversals(multisegment_with_segment: MultisegmentWithSegment) -> None:
    multisegment, segment = multisegment_with_segment

    result = subtract_multisegment_from_segment(segment, multisegment)

    assert are_compounds_similar(
            result, subtract_multisegment_from_segment(
                    segment, reverse_multisegment(multisegment)))
    assert are_compounds_similar(
            result, subtract_multisegment_from_segment(
                    segment, reverse_multisegment_endpoints(multisegment)))
    assert are_compounds_similar(
            result,
            subtract_multisegment_from_segment(reverse_segment(segment),
                                               multisegment))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    subtract_multisegment_from_segment(
                            reverse_segment_coordinates(segment),
                            reverse_multisegment_coordinates(multisegment))))
