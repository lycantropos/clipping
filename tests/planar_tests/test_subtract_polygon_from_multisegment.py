from ground.base import Relation
from hypothesis import given
from orient.planar import (segment_in_multisegment,
                           segment_in_polygon,
                           segment_in_segment)

from clipping.planar import subtract_polygon_from_multisegment
from tests.utils import (PolygonWithMultisegment,
                         are_compounds_similar,
                         is_maybe_linear,
                         pack_non_shaped,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_multisegment_endpoints,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment)
from . import strategies


@given(strategies.polygons_with_multisegments)
def test_basic(polygon_with_multisegment: PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = subtract_polygon_from_multisegment(multisegment, polygon)

    assert is_maybe_linear(result)


@given(strategies.polygons_with_multisegments)
def test_properties(polygon_with_multisegment: PolygonWithMultisegment
                    ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = subtract_polygon_from_multisegment(multisegment, polygon)

    result_points, result_segments = pack_non_shaped(result)
    assert not result_points
    assert all(segment_in_multisegment(segment, multisegment)
               in (Relation.EQUAL, Relation.COMPONENT)
               for segment in result_segments)
    assert all(segment_in_polygon(segment, polygon)
               in (Relation.DISJOINT, Relation.TOUCH)
               for segment in result_segments)
    assert all(segment in result_segments
               or reverse_segment(segment) in result_segments
               # in case of cross
               or any(segment_in_segment(result_segment, segment)
                      is Relation.COMPONENT
                      for result_segment in result_segments)
               for segment in multisegment.segments
               if (segment_in_polygon(segment, polygon)
                   in (Relation.DISJOINT, Relation.CROSS)))


@given(strategies.polygons_with_multisegments)
def test_reversals(polygon_with_multisegment: PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = subtract_polygon_from_multisegment(multisegment, polygon)

    assert result == subtract_polygon_from_multisegment(
            multisegment, reverse_polygon_border(polygon))
    assert result == subtract_polygon_from_multisegment(
            multisegment, reverse_polygon_holes(polygon))
    assert result == subtract_polygon_from_multisegment(
            multisegment, reverse_polygon_holes_contours(polygon))
    assert are_compounds_similar(
            result, subtract_polygon_from_multisegment(
                    reverse_multisegment(multisegment), polygon))
    assert are_compounds_similar(
            result, subtract_polygon_from_multisegment(
                    reverse_multisegment_endpoints(multisegment), polygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    subtract_polygon_from_multisegment(
                            reverse_multisegment_coordinates(multisegment),
                            reverse_polygon_coordinates(polygon))))
