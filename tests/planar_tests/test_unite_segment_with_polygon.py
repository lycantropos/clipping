from ground.base import Relation
from hypothesis import given
from orient.planar import segment_in_polygon

from clipping.planar import unite_segment_with_polygon
from tests.utils import (PolygonWithSegment,
                         are_compounds_similar,
                         is_empty,
                         is_mix,
                         is_polygon,
                         reverse_compound_coordinates,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours,
                         reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.polygons_with_segments)
def test_basic(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = unite_segment_with_polygon(segment, polygon)

    assert is_mix(result) or is_polygon(result)


@given(strategies.polygons_with_segments)
def test_properties(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = unite_segment_with_polygon(segment, polygon)

    relation = segment_in_polygon(segment, polygon)
    assert (not is_mix(result)
            or (relation in (Relation.DISJOINT, Relation.TOUCH, Relation.CROSS)
                and (is_empty(result.discrete) and not is_empty(result.linear)
                     and are_compounds_similar(result.shaped, polygon))))
    assert (not is_polygon(result)
            or relation in (Relation.COMPONENT, Relation.ENCLOSED,
                            Relation.WITHIN))


@given(strategies.polygons_with_segments)
def test_reversals(polygon_with_segment: PolygonWithSegment) -> None:
    polygon, segment = polygon_with_segment

    result = unite_segment_with_polygon(segment, polygon)

    assert are_compounds_similar(
            result, unite_segment_with_polygon(
                    segment, reverse_polygon_border(polygon)))
    assert are_compounds_similar(
            result, unite_segment_with_polygon(segment,
                                               reverse_polygon_holes(polygon)))
    assert are_compounds_similar(
            result, unite_segment_with_polygon(
                    segment, reverse_polygon_holes_contours(polygon)))
    assert are_compounds_similar(
            result, unite_segment_with_polygon(reverse_segment(segment),
                                               polygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    unite_segment_with_polygon(
                            reverse_segment_coordinates(segment),
                            reverse_polygon_coordinates(polygon))))
