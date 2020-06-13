from typing import Tuple

from hypothesis import given
from orient.planar import (Relation,
                           region_in_polygon)

from clipping.core.bounding_box import (intersects_with_polygon,
                                        to_vertices)
from clipping.hints import (BoundingBox,
                            Polygon)
from . import strategies


@given(strategies.polygons_with_bounding_boxes)
def test_basic(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = intersects_with_polygon(bounding_box, polygon)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_self(bounding_box: BoundingBox) -> None:
    assert intersects_with_polygon(bounding_box,
                                   (list(to_vertices(bounding_box)), []))


@given(strategies.polygons_with_bounding_boxes)
def test_equivalents(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]
                     ) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = intersects_with_polygon(bounding_box, polygon)

    assert result is (region_in_polygon(to_vertices(bounding_box), polygon)
                      is not Relation.DISJOINT)
