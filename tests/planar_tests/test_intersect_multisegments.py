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
    left_multisegment, right_multisegment = multisegments_pair

    result = intersect_multisegments(left_multisegment, right_multisegment)

    assert is_maybe_linear(result)


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = intersect_multisegments(multisegment, multisegment)

    assert are_multisegments_equivalent(result, multisegment)


@given(strategies.multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    assert are_multisegments_equivalent(
            intersect_multisegments(
                    left_multisegment,
                    unite_multisegments(left_multisegment,
                                        right_multisegment)),
            left_multisegment)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = intersect_multisegments(left_multisegment, right_multisegment)

    assert result == intersect_multisegments(right_multisegment,
                                             left_multisegment)


@given(strategies.multisegments_triplets)
def test_associativity(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_intersection = intersect_multisegments(left_multisegment,
                                                    mid_multisegment)
    mid_right_intersection = intersect_multisegments(mid_multisegment,
                                                     right_multisegment)
    assert (not is_multisegment(left_mid_intersection)
            or not is_multisegment(mid_right_intersection)
            or (intersect_multisegments(left_mid_intersection,
                                        right_multisegment)
                == intersect_multisegments(left_multisegment,
                                           mid_right_intersection)))


@given(strategies.multisegments_triplets)
def test_difference_operand(multisegments_triplet: MultisegmentsTriplet
                            ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_difference = subtract_multisegments(left_multisegment,
                                                 mid_multisegment)
    left_right_intersection = intersect_multisegments(left_multisegment,
                                                      right_multisegment)
    assert (not is_multisegment(left_mid_difference)
            or not is_multisegment(left_right_intersection)
            or (intersect_multisegments(left_mid_difference,
                                        right_multisegment)
                == subtract_multisegments(left_right_intersection,
                                          mid_multisegment)))


@given(strategies.multisegments_triplets)
def test_distribution_over_union(multisegments_triplet: MultisegmentsTriplet
                                 ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_intersection = intersect_multisegments(left_multisegment,
                                                    mid_multisegment)
    left_right_intersection = intersect_multisegments(left_multisegment,
                                                      right_multisegment)
    assert (not is_multisegment(left_mid_intersection)
            or not is_multisegment(left_right_intersection)
            or are_multisegments_equivalent(
                    intersect_multisegments(
                            left_multisegment,
                            unite_multisegments(mid_multisegment,
                                                right_multisegment)),
                    unite_multisegments(left_mid_intersection,
                                        left_right_intersection)))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = intersect_multisegments(left_multisegment, right_multisegment)

    assert result == intersect_multisegments(
            reverse_multisegment(left_multisegment), right_multisegment)
    assert result == intersect_multisegments(
            left_multisegment, reverse_multisegment(right_multisegment))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(intersect_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
