from ground.hints import Multisegment
from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_compounds_similar,
                         are_multisegments_equivalent,
                         is_maybe_linear,
                         is_multisegment,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = intersect_multisegments(first, second)

    assert is_maybe_linear(result)


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = intersect_multisegments(multisegment, multisegment)

    assert are_multisegments_equivalent(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    assert are_multisegments_equivalent(
            intersect_multisegments(first, unite_multisegments(first, second)),
            first)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = intersect_multisegments(first, second)

    assert result == intersect_multisegments(second, first)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    first_second_intersection = intersect_multisegments(first, second)
    second_third_intersection = intersect_multisegments(second, third)
    assert (not is_multisegment(first_second_intersection)
            or not is_multisegment(second_third_intersection)
            or (intersect_multisegments(first_second_intersection, third)
                == intersect_multisegments(first, second_third_intersection)))


@given(strategies.multisegments_triplets)
def test_difference_operand(multisegments_triplet: MultisegmentsTriplet
                            ) -> None:
    first, second, third = multisegments_triplet

    first_second_difference = subtract_multisegments(first, second)
    first_third_intersection = intersect_multisegments(first, third)
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(first_third_intersection)
            or (intersect_multisegments(first_second_difference, third)
                == subtract_multisegments(first_third_intersection, second)))


@given(strategies.multisegments_triplets)
def test_distribution_over_union(multisegments_triplet: MultisegmentsTriplet
                                 ) -> None:
    first, second, third = multisegments_triplet

    first_second_intersection = intersect_multisegments(first, second)
    first_third_intersection = intersect_multisegments(first, third)
    assert (not is_multisegment(first_second_intersection)
            or not is_multisegment(first_third_intersection)
            or are_multisegments_equivalent(
                    intersect_multisegments(first, unite_multisegments(second,
                                                                       third)),
                    unite_multisegments(first_second_intersection,
                                        first_third_intersection)))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = intersect_multisegments(first, second)

    assert result == intersect_multisegments(
            first, reverse_multisegment(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(intersect_multisegments(
                    reverse_multisegment_coordinates(first),
                    reverse_multisegment_coordinates(second))))
