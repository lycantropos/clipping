from typing import Tuple

from hypothesis import given
from orient.planar import (Relation,
                           region_in_polygon)

from clipping.core.bounding_box import (overlaps_with_polygon,
                                        to_vertices)
from clipping.hints import (BoundingBox,
                            Polygon)
from . import strategies


@given(strategies.polygons_with_bounding_boxes)
def test_basic(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = overlaps_with_polygon(bounding_box, polygon)

    assert isinstance(result, bool)


@given(strategies.polygons_with_bounding_boxes)
def test_equivalents(polygon_with_bounding_box: Tuple[Polygon, BoundingBox]
                     ) -> None:
    polygon, bounding_box = polygon_with_bounding_box

    result = overlaps_with_polygon(bounding_box, polygon)

    assert result is (region_in_polygon(to_vertices(bounding_box), polygon)
                      in (Relation.OVERLAP,
                          Relation.COVER,
                          Relation.ENCLOSES,
                          Relation.EQUAL,
                          Relation.ENCLOSED,
                          Relation.WITHIN))