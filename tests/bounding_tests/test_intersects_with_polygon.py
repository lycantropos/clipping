from typing import Tuple

from ground.base import Context
from ground.hints import (Box,
                          Polygon)
from hypothesis import given
from orient.planar import (Relation,
                           region_in_polygon)

from clipping.core.bounding import (from_contour,
                                    intersects_with_polygon)
from tests.utils import (box_to_contour,
                         box_to_polygon)
from . import strategies


@given(strategies.polygons_with_boxes)
def test_basic(context: Context,
               polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    result = intersects_with_polygon(box, polygon,
                                     context=context)

    assert isinstance(result, bool)


@given(strategies.polygons_with_boxes)
def test_self(context: Context, polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    assert intersects_with_polygon(box, box_to_polygon(box),
                                   context=context)
    assert intersects_with_polygon(from_contour(polygon.border,
                                                context=context), polygon,
                                   context=context)
    assert all(intersects_with_polygon(from_contour(hole,
                                                    context=context),
                                       polygon,
                                       context=context)
               for hole in polygon.holes)


@given(strategies.polygons_with_boxes)
def test_equivalents(context: Context,
                     polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    result = intersects_with_polygon(box, polygon,
                                     context=context)

    assert result is (region_in_polygon(box_to_contour(box), polygon)
                      is not Relation.DISJOINT)
