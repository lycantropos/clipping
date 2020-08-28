from typing import Tuple

from hypothesis import given
from orient.planar import (Relation,
                           contour_in_contour,
                           region_in_region)

from clipping.core.bounding_box import (coupled_with_polygon,
                                        coupled_with_region,
                                        from_points,
                                        to_vertices)
from clipping.core.hints import BoundingBox
from clipping.hints import Region
from tests.utils import equivalence
from . import strategies


@given(strategies.regions_with_bounding_boxes)
def test_basic(region_with_bounding_box: Tuple[Region, BoundingBox]) -> None:
    region, bounding_box = region_with_bounding_box

    result = coupled_with_region(bounding_box, region)

    assert isinstance(result, bool)


@given(strategies.regions_with_bounding_boxes)
def test_self(region_with_bounding_box: Tuple[Region, BoundingBox]) -> None:
    region, bounding_box = region_with_bounding_box

    assert coupled_with_region(bounding_box, list(to_vertices(bounding_box)))
    assert coupled_with_region(from_points(region), region)


@given(strategies.regions_with_bounding_boxes)
def test_equivalents(region_with_bounding_box: Tuple[Region, BoundingBox]
                     ) -> None:
    region, bounding_box = region_with_bounding_box

    result = coupled_with_region(bounding_box, region)

    bounding_box_vertices = to_vertices(bounding_box)
    relation = region_in_region(bounding_box_vertices, region)
    assert equivalence(result,
                       relation in (Relation.OVERLAP,
                                    Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.EQUAL,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN)
                       or relation is Relation.TOUCH
                       and (contour_in_contour(bounding_box_vertices, region)
                            is Relation.OVERLAP))
    assert equivalence(result,
                       coupled_with_polygon(bounding_box, (region, [])))
