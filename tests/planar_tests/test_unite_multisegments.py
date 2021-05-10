from ground.hints import Multisegment
from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_multisegments_equivalent,
                         are_compounds_similar,
                         is_multisegment,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = unite_multisegments(left_multisegment, right_multisegment)

    assert is_multisegment(result)


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = unite_multisegments(multisegment, multisegment)

    assert are_multisegments_equivalent(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = unite_multisegments(left_multisegment,
                                 intersect_multisegments(left_multisegment,
                                                         right_multisegment))

    assert are_multisegments_equivalent(result, left_multisegment)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = unite_multisegments(left_multisegment, right_multisegment)

    assert result == unite_multisegments(right_multisegment, left_multisegment)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = unite_multisegments(
            unite_multisegments(left_multisegment, mid_multisegment),
            right_multisegment)

    assert are_compounds_similar(
            result,
            unite_multisegments(left_multisegment,
                                unite_multisegments(mid_multisegment,
                                                    right_multisegment)))


@given(strategies.multisegments_triplets)
def test_difference_operand(multisegments_triplet: MultisegmentsTriplet
                            ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = unite_multisegments(
            subtract_multisegments(left_multisegment, mid_multisegment),
            right_multisegment)

    assert are_multisegments_equivalent(
            result,
            subtract_multisegments(unite_multisegments(left_multisegment,
                                                       right_multisegment),
                                   subtract_multisegments(mid_multisegment,
                                                          right_multisegment)))


@given(strategies.multisegments_triplets)
def test_distribution_over_intersection(multisegments_triplet
                                        : MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = unite_multisegments(left_multisegment,
                                 intersect_multisegments(mid_multisegment,
                                                         right_multisegment))

    assert are_multisegments_equivalent(
            result,
            intersect_multisegments(unite_multisegments(left_multisegment,
                                                        mid_multisegment),
                                    unite_multisegments(left_multisegment,
                                                        right_multisegment)))


@given(strategies.multisegments_pairs)
def test_equivalents(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = unite_multisegments(left_multisegment, right_multisegment)

    assert result == symmetric_subtract_multisegments(
            symmetric_subtract_multisegments(left_multisegment,
                                             right_multisegment),
            intersect_multisegments(left_multisegment, right_multisegment))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = unite_multisegments(left_multisegment, right_multisegment)

    assert are_compounds_similar(
            result,
            unite_multisegments(reverse_multisegment(left_multisegment),
                                right_multisegment))
    assert are_compounds_similar(
            result,
            unite_multisegments(left_multisegment,
                                reverse_multisegment(right_multisegment)))
    assert are_compounds_similar(
            result, reverse_multisegment_coordinates(unite_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
