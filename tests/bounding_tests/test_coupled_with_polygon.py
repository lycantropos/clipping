from typing import Tuple

from ground.base import Context
from ground.hints import (Box,
                          Polygon)
from hypothesis import given
from orient.planar import (Relation,
                           contour_in_contour,
                           region_in_polygon)

from clipping.core.bounding import (coupled_with_polygon,
                                    from_contour,
                                    is_subset_of_region)
from tests.utils import (box_to_contour,
                         box_to_polygon, equivalence)
from . import strategies


@given(strategies.polygons_with_boxes)
def test_basic(context: Context,
               polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    result = coupled_with_polygon(box, polygon,
                                  context=context)

    assert isinstance(result, bool)


@given(strategies.polygons_with_boxes)
def test_self(context: Context,
              polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    assert coupled_with_polygon(box, box_to_polygon(box),
                                context=context)
    assert coupled_with_polygon(from_contour(polygon.border,
                                             context=context),
                                polygon,
                                context=context)
    assert all(coupled_with_polygon(from_contour(hole,
                                                 context=context),
                                    polygon,
                                    context=context)
               or is_subset_of_region(from_contour(hole,
                                                   context=context), hole,
                                      context=context)
               for hole in polygon.holes)


@given(strategies.polygons_with_boxes)
def test_equivalents(context: Context,
                     polygon_with_box: Tuple[Polygon, Box]) -> None:
    polygon, box = polygon_with_box

    result = coupled_with_polygon(box, polygon,
                                  context=context)

    box_contour = box_to_contour(box)
    relation = region_in_polygon(box_contour, polygon)
    assert equivalence(result,
                       relation in (Relation.OVERLAP,
                                    Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.EQUAL,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN)
                       or relation is Relation.TOUCH
                       and (contour_in_contour(box_contour, polygon.border)
                            is Relation.OVERLAP
                            or any(contour_in_contour(box_contour,
                                                      hole) is Relation.OVERLAP
                                   for hole in polygon.holes)))
