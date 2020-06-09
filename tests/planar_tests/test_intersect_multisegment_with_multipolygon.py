from hypothesis import given
from orient.planar import (Relation,
                           point_in_multipolygon,
                           point_in_multisegment,
                           segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.core.utils import (sort_pair,
                                 to_rational_multipolygon,
                                 to_rational_multisegment)
from clipping.planar import intersect_multisegment_with_multipolygon
from tests.utils import (MultipolygonWithMultisegment,
                         is_mix,
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

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    assert is_mix(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    result_multipoint, result_multisegment, result_multipolygon = result
    rational_multisegment = to_rational_multisegment(multisegment)
    rational_multipolygon = to_rational_multipolygon(multipolygon)
    assert all(point_in_multisegment(point, multisegment)
               is Relation.COMPONENT
               for point in result_multipoint)
    assert all(point_in_multipolygon(point, multipolygon)
               is Relation.COMPONENT
               for point in result_multipoint)
    assert all(segment_in_multisegment(segment, rational_multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_multisegment)
    assert all(segment_in_multipolygon(segment, rational_multipolygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for segment in result_multisegment)
    assert not result_multipolygon
    assert all(sort_pair(segment) in result_multisegment
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_multisegment)
               for segment in rational_multisegment
               if (segment_in_multipolygon(segment, rational_multipolygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


@given(strategies.empty_multipolygons_with_multisegments)
def test_left_absorbing_element(empty_multipolygon_with_multisegment
                                : MultipolygonWithMultisegment) -> None:
    empty_multipolygon, multisegment = empty_multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      empty_multipolygon)

    assert not any(result)


@given(strategies.multipolygons_with_empty_multisegments)
def test_right_absorbing_element(multipolygon_with_empty_multisegment
                                 : MultipolygonWithMultisegment) -> None:
    multipolygon, empty_multisegment = multipolygon_with_empty_multisegment

    result = intersect_multisegment_with_multipolygon(empty_multisegment,
                                                      multipolygon)

    assert not any(result)


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
