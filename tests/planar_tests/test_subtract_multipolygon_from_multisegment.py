from ground.base import Relation
from hypothesis import given
from orient.planar import (segment_in_multipolygon,
                           segment_in_multisegment,
                           segment_in_segment)

from clipping.planar import subtract_multipolygon_from_multisegment
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
                         reverse_segment)
from . import strategies


@given(strategies.multipolygons_with_multisegments)
def test_basic(multipolygon_with_multisegment: MultipolygonWithMultisegment
               ) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     multipolygon)

    assert is_maybe_linear(result)


@given(strategies.multipolygons_with_multisegments)
def test_properties(multipolygon_with_multisegment
                    : MultipolygonWithMultisegment) -> None:
    multipolygon, multisegment = multipolygon_with_multisegment

    result = subtract_multipolygon_from_multisegment(multisegment,
                                                     multipolygon)

    result_points, result_segments = pack_non_shaped(result)
    assert not result_points
    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_multipolygon(segment, multipolygon)
               in (Relation.DISJOINT, Relation.TOUCH)
               for segment in result_segments)
    assert all(segment in result_segments
               or reverse_segment(segment) in result_segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_multipolygon(segment, multipolygon)
                   in (Relation.DISJOINT, Relation.CROSS)))


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
    assert are_compounds_similar(
            result, subtract_multipolygon_from_multisegment(
                    reverse_multisegment(multisegment), multipolygon))
    assert are_compounds_similar(
            result, subtract_multipolygon_from_multisegment(
                    reverse_multisegment_endpoints(multisegment),
                    multipolygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    subtract_multipolygon_from_multisegment(
                            reverse_multisegment_coordinates(multisegment),
                            reverse_multipolygon_coordinates(multipolygon))))
