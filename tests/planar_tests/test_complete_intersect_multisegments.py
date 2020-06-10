from hypothesis import given

from clipping.hints import Multisegment
from clipping.planar import (complete_intersect_multisegments,
                             intersect_multisegments,
                             unite_multisegments)
from tests.utils import (MultisegmentsPair,
                         is_mix,
                         mix_equivalent_to_multisegment,
                         reverse_multisegment)
from . import strategies


@given(strategies.multisegments_pairs)
def test_basic(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert is_mix(result)


@given(strategies.multisegments)
def test_idempotence(multisegment: Multisegment) -> None:
    result = complete_intersect_multisegments(multisegment, multisegment)

    assert mix_equivalent_to_multisegment(result, multisegment)


@given(strategies.empty_multisegments_with_multisegments)
def test_left_absorbing_element(empty_multisegment_with_multisegment
                                : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(empty_multisegment, multisegment)

    assert not any(result)


@given(strategies.empty_multisegments_with_multisegments)
def test_right_absorbing_element(empty_multisegment_with_multisegment
                                 : MultisegmentsPair) -> None:
    empty_multisegment, multisegment = empty_multisegment_with_multisegment

    result = complete_intersect_multisegments(multisegment, empty_multisegment)

    assert not any(result)


@given(strategies.rational_multisegments_pairs)
def test_absorption_identity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(
            left_multisegment,
            unite_multisegments(left_multisegment, right_multisegment))

    assert mix_equivalent_to_multisegment(result, left_multisegment)


@given(strategies.multisegments_pairs)
def test_commutativity(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    assert result == complete_intersect_multisegments(right_multisegment,
                                                      left_multisegment)


@given(strategies.multisegments_pairs)
def test_connection_with_intersect(multisegments_pair: MultisegmentsPair
                                   ) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)

    _, multisegment, _ = result
    assert multisegment == intersect_multisegments(left_multisegment,
                                                   right_multisegment)


@given(strategies.multisegments_pairs)
def test_reversals(multisegments_pair: MultisegmentsPair) -> None:
    left_multisegment, right_multisegment = multisegments_pair

    result = complete_intersect_multisegments(left_multisegment,
                                              right_multisegment)
    assert result == complete_intersect_multisegments(
            reverse_multisegment(left_multisegment), right_multisegment)
    assert result == complete_intersect_multisegments(
            left_multisegment, reverse_multisegment(right_multisegment))
