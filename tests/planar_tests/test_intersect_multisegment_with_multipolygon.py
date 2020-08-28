from hypothesis import given
from orient.planar import (Relation,
                           segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import intersect_multisegment_with_multipolygon
from tests.utils import (MultipolygonWithMultisegment,
                         is_multisegment,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multisegment,
                         reverse_multisegment_endpoints,
                         sort_pair)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment: MultipolygonWithMultisegment
               ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    assert is_multisegment(result)


@given(strategies.rational_multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result)
    assert all(segment_in_multipolygon(segment, multipolygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for segment in result)
    assert all(sort_pair(segment) in result
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result)
               for segment in multisegment
               if (segment_in_multipolygon(segment, multipolygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


@given(strategies.empty_multipolygons_with_multisegments)
def test_left_absorbing_element(empty_multipolygon_with_multisegment
                                : MultipolygonWithMultisegment) -> None:
    empty_multipolygon, multisegment = empty_multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      empty_multipolygon)

    assert not result


@given(strategies.multipolygons_with_empty_multisegments)
def test_right_absorbing_element(multipolygon_with_empty_multisegment
                                 : MultipolygonWithMultisegment) -> None:
    multipolygon, empty_multisegment = multipolygon_with_empty_multisegment

    result = intersect_multisegment_with_multipolygon(empty_multisegment,
                                                      multipolygon)

    assert not result


@given(strategies.multipolygons_with_multisegments)
def test_reversals(multipolygon_with_multisegment: MultipolygonWithMultisegment
                   ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    assert result == intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon(multipolygon))
    assert result == intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_borders(multipolygon))
    assert result == intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_holes(multipolygon))
    assert result == intersect_multisegment_with_multipolygon(
            multisegment, reverse_multipolygon_holes_contours(multipolygon))
    assert result == intersect_multisegment_with_multipolygon(
            reverse_multisegment(multisegment), multipolygon)
    assert result == intersect_multisegment_with_multipolygon(
            reverse_multisegment_endpoints(multisegment), multipolygon)
