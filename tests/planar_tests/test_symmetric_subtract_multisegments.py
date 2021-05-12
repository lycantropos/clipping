from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             symmetric_subtract_multisegments,
                             unite_multisegments)
from tests.utils import (Multisegment,
                         MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_compounds_similar,
                         are_multisegments_equivalent,
                         is_empty,
                         is_maybe_linear,
                         is_multisegment,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = symmetric_subtract_multisegments(first, second)

    assert is_maybe_linear(result)


@given(strategies.multisegments)
def test_self_inverse(multisegment: Multisegment) -> None:
    result = symmetric_subtract_multisegments(multisegment, multisegment)

    assert is_empty(result)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = symmetric_subtract_multisegments(first, second)

    assert result == symmetric_subtract_multisegments(second, first)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    first_second_symmetric_difference = symmetric_subtract_multisegments(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_multisegments(
            second, third)
    assert (not is_multisegment(first_second_symmetric_difference)
            or not is_multisegment(second_third_symmetric_difference)
            or are_multisegments_equivalent(
                    symmetric_subtract_multisegments(
                            first_second_symmetric_difference, third),
                    symmetric_subtract_multisegments(
                            first, second_third_symmetric_difference)))


@given(strategies.multisegments_triplets)
def test_repeated(multisegments_triplet: MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    first_second_symmetric_difference = symmetric_subtract_multisegments(
            first, second)
    second_third_symmetric_difference = symmetric_subtract_multisegments(
            second, third)
    assert (not is_multisegment(first_second_symmetric_difference)
            or not is_multisegment(second_third_symmetric_difference)
            or are_multisegments_equivalent(
                    symmetric_subtract_multisegments(
                            first_second_symmetric_difference,
                            second_third_symmetric_difference),
                    symmetric_subtract_multisegments(first, third)))


@given(strategies.multisegments_pairs)
def test_equivalents(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = symmetric_subtract_multisegments(first, second)

    first_second_difference = subtract_multisegments(first, second)
    second_first_difference = subtract_multisegments(second, first)
    second_first_intersection = intersect_multisegments(second, first)
    assert (not is_multisegment(second_first_intersection)
            or result == subtract_multisegments(
                    unite_multisegments(first, second),
                    second_first_intersection))
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(second_first_difference)
            or result == unite_multisegments(first_second_difference,
                                             second_first_difference))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = symmetric_subtract_multisegments(first, second)

    assert are_compounds_similar(
            result, symmetric_subtract_multisegments(
                    first, reverse_multisegment(second)))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(symmetric_subtract_multisegments(
                    reverse_multisegment_coordinates(first),
                    reverse_multisegment_coordinates(second))))
