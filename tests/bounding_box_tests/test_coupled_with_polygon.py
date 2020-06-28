from typing import Tuple

from hypothesis import given
from orient.planar import (Relation,
                           contour_in_contour,
                           region_in_polygon)

from clipping.core.bounding_box import (coupled_with_polygon,
                                        from_points,
                                        is_subset_of_region,
                                        to_vertices)
from clipping.core.hints import BoundingBox
from clipping.hints import Polygon
from tests.utils import equivalence
from . import strategies


@given(strategies.polygons_with_bounding_boxes)
def test_basic(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = coupled_with_polygon(bounding_box, polygon)

    assert isinstance(result, bool)


@given(strategies.polygons_with_bounding_boxes)
def test_self(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    border, holes = polygon
    assert coupled_with_polygon(bounding_box,
                                (list(to_vertices(bounding_box)), []))
    assert coupled_with_polygon(from_points(border), polygon)
    assert all(coupled_with_polygon(from_points(hole), polygon)
               or is_subset_of_region(from_points(hole), hole)
               for hole in holes)


@given(strategies.polygons_with_bounding_boxes)
def test_equivalents(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]
                     ) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = coupled_with_polygon(bounding_box, polygon)

    border, holes = polygon
    bounding_box_vertices = to_vertices(bounding_box)
    relation = region_in_polygon(bounding_box_vertices, polygon)
    assert equivalence(result,
                       relation in (Relation.OVERLAP,
                                    Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.EQUAL,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN)
                       or relation is Relation.TOUCH
                       and (contour_in_contour(bounding_box_vertices, border)
                            is Relation.OVERLAP
                            or any(contour_in_contour(bounding_box_vertices,
                                                      hole) is Relation.OVERLAP
                                   for hole in holes)))
