from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from tests.utils import (Multisegment,
                         MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_multisegments_equivalent,
                         are_multisegments_similar,
                         is_multisegment,
                         reverse_multisegment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_multisegment(result)


@given(strategies.multisegments)
def test_self_inverse(multisegment: Multisegment) -> None:
    result = symmetric_subtract_multisegments(multisegment, multisegment)

    assert not result.segments


@given(strategies.empty_multisegments_with_multisegments)
def test_left_neutral_element(empty_multisegment_with_multisegment
                              : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = symmetric_subtract_multisegments(empty_multisegment, multisegment)

    assert are_multisegments_similar(result, multisegment)


@given(strategies.empty_multisegments_with_multisegments)
def test_right_neutral_element(empty_multisegment_with_multisegment
                               : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = symmetric_subtract_multisegments(multisegment, empty_multisegment)

    assert are_multisegments_similar(result, multisegment)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert result == symmetric_subtract_multisegments(right_multisegment,
                                                      left_multisegment)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = symmetric_subtract_multisegments(
            symmetric_subtract_multisegments(left_multisegment,
                                             mid_multisegment),
            right_multisegment)

    assert are_multisegments_equivalent(
            result,
            symmetric_subtract_multisegments(
                    left_multisegment,
                    symmetric_subtract_multisegments(mid_multisegment,
                                                     right_multisegment)))


@given(strategies.multisegments_triplets)
def test_repeated(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = symmetric_subtract_multisegments(
            symmetric_subtract_multisegments(left_multisegment,
                                             mid_multisegment),
            symmetric_subtract_multisegments(mid_multisegment,
                                             right_multisegment))

    assert are_multisegments_equivalent(
            result,
            symmetric_subtract_multisegments(left_multisegment,
                                             right_multisegment))


@given(strategies.multisegments_pairs)
def test_equivalents(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert result == subtract_multisegments(
            unite_multisegments(left_multisegment, right_multisegment),
            intersect_multisegments(right_multisegment, left_multisegment))
    assert result == unite_multisegments(
            subtract_multisegments(left_multisegment, right_multisegment),
            subtract_multisegments(right_multisegment, left_multisegment))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert are_multisegments_similar(
            result, symmetric_subtract_multisegments(
                    reverse_multisegment(left_multisegment),
                    right_multisegment))
    assert are_multisegments_similar(
            result,
            symmetric_subtract_multisegments(left_multisegment,
                                             reverse_multisegment(
                                                     right_multisegment)))
