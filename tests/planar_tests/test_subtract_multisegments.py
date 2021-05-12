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
    first, second = multisegments_pair

    result = subtract_multisegments(first, second)

    assert is_maybe_linear(result)


@given(strategies.multisegments_pairs)
def test_commutative_case(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = subtract_multisegments(first, second)

    assert equivalence(result == subtract_multisegments(second, first),
                       are_multisegments_equivalent(first, second))


@given(strategies.multisegments_triplets)
def test_difference_subtrahend(multisegments_triplet: MultisegmentsTriplet
                               ) -> None:
    first, second, third = multisegments_triplet

    first_second_difference = subtract_multisegments(first, second)
    first_third_difference = intersect_multisegments(first, third)
    second_third_difference = subtract_multisegments(second, third)
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(first_third_difference)
            or not is_multisegment(second_third_difference)
            or are_multisegments_equivalent(
                    subtract_multisegments(first, second_third_difference),
                    unite_multisegments(first_second_difference,
                                        first_third_difference)))


@given(strategies.multisegments_triplets)
def test_intersection_minuend(multisegments_triplet: MultisegmentsTriplet
                              ) -> None:
    first, second, third = multisegments_triplet

    first_second_intersection = intersect_multisegments(first, second)
    second_third_difference = subtract_multisegments(second, third)
    assert (not is_multisegment(first_second_intersection)
            or not is_multisegment(second_third_difference)
            or (subtract_multisegments(first_second_intersection, third)
                == intersect_multisegments(first, second_third_difference)))


@given(strategies.multisegments_triplets)
def test_intersection_subtrahend(multisegments_triplet: MultisegmentsTriplet
                                 ) -> None:
    first, second, third = multisegments_triplet

    first_second_difference = subtract_multisegments(first, second)
    first_third_difference = subtract_multisegments(first, third)
    second_third_intersection = intersect_multisegments(second, third)
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(first_third_difference)
            or not is_multisegment(second_third_intersection)
            or are_multisegments_equivalent(
                    subtract_multisegments(first, second_third_intersection),
                    unite_multisegments(first_second_difference,
                                        first_third_difference)))


@given(strategies.multisegments_triplets)
def test_union_subtrahend(multisegments_triplet: MultisegmentsTriplet) -> None:
    first, second, third = multisegments_triplet

    first_second_difference = subtract_multisegments(first, second)
    first_third_difference = subtract_multisegments(first, third)
    assert (not is_multisegment(first_second_difference)
            or not is_multisegment(first_third_difference)
            or are_compounds_similar(
                    subtract_multisegments(first,
                                           unite_multisegments(second, third)),
                    intersect_multisegments(first_second_difference,
                                            first_third_difference)))


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    first, second = multisegments_pair

    result = subtract_multisegments(first, second)

    assert are_compounds_similar(
            result, subtract_multisegments(reverse_multisegment(first),
                                           second))
    assert result == subtract_multisegments(first,
                                            reverse_multisegment(second))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(subtract_multisegments(
                    reverse_multisegment_coordinates(first),
                    reverse_multisegment_coordinates(second))))
