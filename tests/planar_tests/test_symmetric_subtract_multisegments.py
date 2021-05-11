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
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_maybe_linear(result)


@given(strategies.multisegments)
def test_self_inverse(multisegment: Multisegment) -> None:
    result = symmetric_subtract_multisegments(multisegment, multisegment)

    assert is_empty(result)


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

    left_mid_symmetric_difference = symmetric_subtract_multisegments(
            left_multisegment, mid_multisegment)
    mid_right_symmetric_difference = symmetric_subtract_multisegments(
            mid_multisegment, right_multisegment)
    assert (not is_multisegment(left_mid_symmetric_difference)
            or not is_multisegment(mid_right_symmetric_difference)
            or are_multisegments_equivalent(
                    symmetric_subtract_multisegments(
                            left_mid_symmetric_difference,
                            right_multisegment),
                    symmetric_subtract_multisegments(
                            left_multisegment,
                            mid_right_symmetric_difference)))


@given(strategies.multisegments_triplets)
def test_repeated(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_symmetric_difference = symmetric_subtract_multisegments(
            left_multisegment, mid_multisegment)
    mid_right_symmetric_difference = symmetric_subtract_multisegments(
            mid_multisegment, right_multisegment)
    assert (not is_multisegment(left_mid_symmetric_difference)
            or not is_multisegment(mid_right_symmetric_difference)
            or are_multisegments_equivalent(
                    symmetric_subtract_multisegments(
                            left_mid_symmetric_difference,
                            mid_right_symmetric_difference),
                    symmetric_subtract_multisegments(left_multisegment,
                                                     right_multisegment)))


@given(strategies.multisegments_pairs)
def test_equivalents(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    left_right_difference = subtract_multisegments(left_multisegment,
                                                   right_multisegment)
    right_left_difference = subtract_multisegments(right_multisegment,
                                                   left_multisegment)
    right_left_intersection = intersect_multisegments(right_multisegment,
                                                      left_multisegment)
    assert (not is_multisegment(right_left_intersection)
            or result == subtract_multisegments(
                    unite_multisegments(left_multisegment, right_multisegment),
                    right_left_intersection))
    assert (not is_multisegment(left_right_difference)
            or not is_multisegment(right_left_difference)
            or result == unite_multisegments(left_right_difference,
                                             right_left_difference))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = symmetric_subtract_multisegments(left_multisegment,
                                              right_multisegment)

    assert are_compounds_similar(
            result, symmetric_subtract_multisegments(
                    reverse_multisegment(left_multisegment),
                    right_multisegment))
    assert are_compounds_similar(
            result,
            symmetric_subtract_multisegments(left_multisegment,
                                             reverse_multisegment(
                                                     right_multisegment)))
    assert are_compounds_similar(
            result,
            reverse_compound_coordinates(symmetric_subtract_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
