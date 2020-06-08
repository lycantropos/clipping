from hypothesis import given
from orient.planar import (Relation,
                           segment_in_multipolygon,
                           segment_in_multisegment)

from clipping.core.utils import (to_rational_multipolygon,
                                 to_rational_multisegment)
from clipping.planar import subtract_multipolygon_from_multisegment
from tests.utils import (MultipolygonWithMultisegment,
                         are_multisegments_similar,
                         is_multisegment,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multisegment,
                         reverse_multisegment_endpoints)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment: MultipolygonWithMultisegment
               ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     multipolygon)

    assert is_multisegment(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     multipolygon)

    rational_multisegment = to_rational_multisegment(multisegment)
    rational_multipolygon = to_rational_multipolygon(multipolygon)
    assert all(segment_in_multisegment(segment, rational_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result)
    assert all(segment_in_multipolygon(segment, rational_multipolygon)
               is (Relation.DISJOINT, Relation.TOUCH)
               for segment in result)


@given(strategies.empty_multipolygons_with_multisegments)
def test_left_neutral_element(empty_multipolygon_with_multisegment
                              : MultipolygonWithMultisegment) -> None:
    empty_multipolygon, multisegment = empty_multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     empty_multipolygon)

    assert result == multisegment


@given(strategies.multipolygons_with_empty_multisegments)
def test_right_absorbing_element(multipolygon_with_empty_multisegment
                                 : MultipolygonWithMultisegment) -> None:
    multipolygon, empty_multisegment = multipolygon_with_empty_multisegment

    result = subtract_multipolygon_from_multisegment(empty_multisegment,
                                                     multipolygon)

    assert not result


@given(strategies.multipolygons_with_multisegments)
def test_reversals(multipolygon_with_multisegment: MultipolygonWithMultisegment
                   ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     multipolygon)

    assert result == subtract_multipolygon_from_multisegment(
            multisegment, reverse_multipolygon(multipolygon))
    assert result == subtract_multipolygon_from_multisegment(
            multisegment, reverse_multipolygon_borders(multipolygon))
    assert result == subtract_multipolygon_from_multisegment(
            multisegment, reverse_multipolygon_holes(multipolygon))
    assert result == subtract_multipolygon_from_multisegment(
            multisegment, reverse_multipolygon_holes_contours(multipolygon))
    assert are_multisegments_similar(
            result, subtract_multipolygon_from_multisegment(
                    reverse_multisegment(multisegment), multipolygon))
    assert are_multisegments_similar(
            result, subtract_multipolygon_from_multisegment(
                    reverse_multisegment_endpoints(multisegment),
                    multipolygon))
