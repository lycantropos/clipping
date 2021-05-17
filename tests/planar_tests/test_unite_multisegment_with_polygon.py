from ground.base import Relation
from hypothesis import given
from orient.planar import multisegment_in_polygon

from clipping.planar import unite_multisegment_with_polygon
from tests.utils import (PolygonWithMultisegment,
                         are_compounds_similar,
                         is_empty,
                         is_mix,
                         is_polygon,
                         reverse_compound_coordinates,
                         reverse_multisegment,
                         reverse_multisegment_coordinates,
                         reverse_multisegment_endpoints,
                         reverse_polygon_border,
                         reverse_polygon_coordinates,
                         reverse_polygon_holes,
                         reverse_polygon_holes_contours)
from . import strategies


@given(strategies.polygons_with_multisegments)
def test_basic(polygon_with_multisegment: PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = unite_multisegment_with_polygon(multisegment, polygon)

    assert is_mix(result) or is_polygon(result)


@given(strategies.polygons_with_multisegments)
def test_properties(polygon_with_multisegment: PolygonWithMultisegment
                    ) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = unite_multisegment_with_polygon(multisegment, polygon)

    relation = multisegment_in_polygon(multisegment, polygon)
    assert (not is_mix(result)
            or (relation in (Relation.DISJOINT, Relation.TOUCH, Relation.CROSS)
                and (is_empty(result.discrete) and not is_empty(result.linear)
                     and are_compounds_similar(result.shaped, polygon))))
    assert (not is_polygon(result)
            or relation in (Relation.COMPONENT, Relation.ENCLOSED,
                            Relation.WITHIN))


@given(strategies.polygons_with_multisegments)
def test_reversals(polygon_with_multisegment: PolygonWithMultisegment) -> None:
    polygon, multisegment = polygon_with_multisegment

    result = unite_multisegment_with_polygon(multisegment, polygon)

    assert result == unite_multisegment_with_polygon(
            multisegment, reverse_polygon_border(polygon))
    assert result == unite_multisegment_with_polygon(
            multisegment, reverse_polygon_holes(polygon))
    assert result == unite_multisegment_with_polygon(
            multisegment, reverse_polygon_holes_contours(polygon))
    assert are_compounds_similar(
            result, unite_multisegment_with_polygon(
                    reverse_multisegment(multisegment), polygon))
    assert are_compounds_similar(
            result, unite_multisegment_with_polygon(
                    reverse_multisegment_endpoints(multisegment), polygon))
    assert are_compounds_similar(
            result, reverse_compound_coordinates(
                    unite_multisegment_with_polygon(
                            reverse_multisegment_coordinates(multisegment),
                            reverse_polygon_coordinates(polygon))))
