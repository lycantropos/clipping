from ground.hints import Multisegment
from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_compounds_similar,
                         are_multisegments_equivalent,
                         is_multisegment,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = unite_multisegments(first, second)

    assert is_multisegment(result)


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = unite_multisegments(multisegment, multisegment)

    assert are_multisegments_equivalent(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    first_second_intersection = intersect_multisegments(first, second)
    assert (not is_multisegment(first_second_intersection)
            or are_multisegments_equivalent(
                    unite_multisegments(first, first_second_intersection),
                    first))


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = unite_multisegments(first, second)

    assert result == unite_multisegments(second, first)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    result = unite_multisegments(unite_multisegments(first, second), third)

    assert are_compounds_similar(
            result,
            unite_multisegments(first, unite_multisegments(second, third)))


@given(strategies.multisegments_triplets)
def test_difference_operand(multisegments_triplet: MultisegmentsTriplet
                            ) -> None:
    first, second, third = multisegments_triplet

    first_second_difference = subtract_multisegments(first, second)
    second_third_difference = subtract_multisegments(second, third)
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(second_third_difference)
            or are_multisegments_equivalent(
                    unite_multisegments(first_second_difference, third),
                    subtract_multisegments(unite_multisegments(first, third),
                                           second_third_difference)))


@given(strategies.multisegments_triplets)
def test_distribution_over_intersection(multisegments_triplet
                                        : MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    second_third_intersection = intersect_multisegments(second, third)
    assert (not is_multisegment(second_third_intersection)
            or are_multisegments_equivalent(
                    unite_multisegments(first, second_third_intersection),
                    intersect_multisegments(unite_multisegments(first, second),
                                            unite_multisegments(first,
                                                                third))))


@given(strategies.multisegments_pairs)
def test_equivalents(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = unite_multisegments(first, second)

    first_second_symmetric_difference = symmetric_subtract_multisegments(
            first, second)
    first_second_intersection = intersect_multisegments(first, second)
    assert (not is_multisegment(first_second_symmetric_difference)
            or not is_multisegment(first_second_intersection)
            or result == symmetric_subtract_multisegments(
                    first_second_symmetric_difference,
                    first_second_intersection))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = unite_multisegments(first, second)

    assert are_compounds_similar(
            result, unite_multisegments(first, reverse_multisegment(second)))
    assert are_compounds_similar(
            result, reverse_multisegment_coordinates(unite_multisegments(
                    reverse_multisegment_coordinates(first),
                    reverse_multisegment_coordinates(second))))
