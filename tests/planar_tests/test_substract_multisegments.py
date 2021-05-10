from hypothesis import given

from clipping.planar import (intersect_multisegments,
                             subtract_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         MultisegmentsTriplet,
                         are_multisegments_equivalent,
                         are_compounds_similar,
                         equivalence,
                         is_multisegment,
                         reverse_multisegment,
                         reverse_multisegment_coordinates)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = subtract_multisegments(left_multisegment, right_multisegment)

    assert is_multisegment(result)


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

    result = subtract_multisegments(left_multisegment,
                                    subtract_multisegments(mid_multisegment,
                                                           right_multisegment))

    assert are_multisegments_equivalent(
            result,
            unite_multisegments(subtract_multisegments(left_multisegment,
                                                       mid_multisegment),
                                intersect_multisegments(left_multisegment,
                                                        right_multisegment)))


@given(strategies.multisegments_triplets)
def test_intersection_minuend(multisegments_triplet: MultisegmentsTriplet
                              ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = subtract_multisegments(intersect_multisegments(left_multisegment,
                                                            mid_multisegment),
                                    right_multisegment)

    assert result == intersect_multisegments(
            left_multisegment, subtract_multisegments(mid_multisegment,
                                                      right_multisegment))


@given(strategies.multisegments_triplets)
def test_intersection_subtrahend(multisegments_triplet: MultisegmentsTriplet
                                 ) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = subtract_multisegments(
            left_multisegment, intersect_multisegments(mid_multisegment,
                                                       right_multisegment))

    assert are_multisegments_equivalent(
            result,
            unite_multisegments(subtract_multisegments(left_multisegment,
                                                       mid_multisegment),
                                subtract_multisegments(left_multisegment,
                                                       right_multisegment)))


@given(strategies.multisegments_triplets)
def test_union_subtrahend(multisegments_triplet: MultisegmentsTriplet) -> None:
    (left_multisegment, mid_multisegment,
     right_multisegment) = multisegments_triplet

    result = subtract_multisegments(left_multisegment,
                                    unite_multisegments(mid_multisegment,
                                                        right_multisegment))

    assert are_compounds_similar(
            result, intersect_multisegments(
                    subtract_multisegments(left_multisegment,
                                           mid_multisegment),
                    subtract_multisegments(left_multisegment,
                                           right_multisegment)))


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
            result,
            reverse_multisegment_coordinates(subtract_multisegments(
                    reverse_multisegment_coordinates(left_multisegment),
                    reverse_multisegment_coordinates(right_multisegment))))
