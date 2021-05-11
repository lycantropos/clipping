from ground.base import Relation
from hypothesis import given
from orient.planar import (segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import intersect_multisegment_with_multipolygon
from tests.utils import (MultipolygonWithMultisegment,
                         are_compounds_similar,
                         is_maybe_linear,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_multipolygon,
                         reverse_multipolygon_borders,
                         reverse_multipolygon_coordinates,
                         reverse_multipolygon_holes,
                         reverse_multipolygon_holes_contours,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_multisegment_endpoints,
                         to_sorted_segment)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment: MultipolygonWithMultisegment
               ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    assert is_maybe_linear(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = intersect_multisegment_with_multipolygon(multisegment,
                                                      multipolygon)

    result_points, result_segments = pack_non_shaped(result)
    assert not result_points
    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_multipolygon(segment, multipolygon)
               in (Relation.COMPONENT, Relation.ENCLOSED, Relation.WITHIN)
               for segment in result_segments)
    assert all(to_sorted_segment(segment) in result_segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   in (Relation.CROSS, Relation.COMPONENT, Relation.ENCLOSED,
                       Relation.WITHIN)))


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
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    intersect_multisegment_with_multipolygon(
                            reverse_multisegment_coordinates(multisegment),
                            reverse_multipolygon_coordinates(multipolygon))))
