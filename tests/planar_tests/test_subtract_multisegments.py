from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_compounds_similar,
                         are_multisegments_equivalent,
                         equivalence,
                         is_maybe_linear,
                         is_multisegment,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = subtract_multisegments(left_multisegment, right_multisegment)

    assert is_maybe_linear(result)


@given(strategies.multisegments_pairs)
def test_commutative_case(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = subtract_multisegments(left_multisegment, right_multisegment)

    assert equivalence(result == subtract_multisegments(right_multisegment,
                                                        left_multisegment),
                       are_multisegments_equivalent(left_multisegment,
                                                    right_multisegment))


@given(strategies.multisegments_triplets)
def test_difference_subtrahend(multisegments_triplet: MultisegmentsTriplet
                               ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_difference = subtract_multisegments(left_multisegment,
                                                 mid_multisegment)
    left_right_difference = intersect_multisegments(left_multisegment,
                                                    right_multisegment)
    mid_right_difference = subtract_multisegments(mid_multisegment,
                                                  right_multisegment)
    assert (not is_multisegment(left_mid_difference)
            or not is_multisegment(left_right_difference)
            or not is_multisegment(mid_right_difference)
            or are_multisegments_equivalent(
                    subtract_multisegments(left_multisegment,
                                           mid_right_difference),
                    unite_multisegments(left_mid_difference,
                                        left_right_difference)))


@given(strategies.multisegments_triplets)
def test_intersection_minuend(multisegments_triplet: MultisegmentsTriplet
                              ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_intersection = intersect_multisegments(left_multisegment,
                                                    mid_multisegment)
    mid_right_difference = subtract_multisegments(mid_multisegment,
                                                  right_multisegment)
    assert (not is_multisegment(left_mid_intersection)
            or not is_multisegment(mid_right_difference)
            or (subtract_multisegments(left_mid_intersection,
                                       right_multisegment)
                == intersect_multisegments(left_multisegment,
                                           mid_right_difference)))


@given(strategies.multisegments_triplets)
def test_intersection_subtrahend(multisegments_triplet: MultisegmentsTriplet
                                 ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_difference = subtract_multisegments(left_multisegment,
                                                 mid_multisegment)
    left_right_difference = subtract_multisegments(left_multisegment,
                                                   right_multisegment)
    mid_right_intersection = intersect_multisegments(mid_multisegment,
                                                     right_multisegment)
    assert (not is_multisegment(left_mid_difference)
            or not is_multisegment(left_right_difference)
            or not is_multisegment(mid_right_intersection)
            or are_multisegments_equivalent(
                    subtract_multisegments(left_multisegment,
                                           mid_right_intersection),
                    unite_multisegments(left_mid_difference,
                                        left_right_difference)))


@given(strategies.multisegments_triplets)
def test_union_subtrahend(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    left_mid_difference = subtract_multisegments(left_multisegment,
                                                 mid_multisegment)
    left_right_difference = subtract_multisegments(left_multisegment,
                                                   right_multisegment)
    assert (not is_multisegment(left_mid_difference)
            or not is_multisegment(left_right_difference)
            or are_compounds_similar(
                    subtract_multisegments(
                            left_multisegment,
                            unite_multisegments(mid_multisegment,
                                                right_multisegment)),
                    intersect_multisegments(left_mid_difference,
                                            left_right_difference)))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = subtract_multisegments(left_multisegment, right_multisegment)

    assert are_compounds_similar(
            result,
            subtract_multisegments(reverse_multisegment(left_multisegment),
                                   right_multisegment))
    assert result == subtract_multisegments(
            left_multisegment, reverse_multisegment(right_multisegment))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
