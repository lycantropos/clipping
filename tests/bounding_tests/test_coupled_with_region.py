from typing import Tuple

from ground.base import Context
from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           contour_in_contour,
                           region_in_region)

from clipping.core.bounding import (coupled_with_polygon,
                                    coupled_with_region,
                                    from_contour)
from clipping.hints import Region
from tests.utils import (box_to_contour,
                         contour_to_polygon,
                         equivalence)
from . import strategies


@given(strategies.regions_with_boxes)
def test_basic(context: Context, region_with_box: Tuple[Region, Box]) -> None:
    region, box = region_with_box

    result = coupled_with_region(box, region,
                                 context=context)

    assert isinstance(result, bool)


@given(strategies.regions_with_boxes)
def test_self(context: Context, region_with_box: Tuple[Region, Box]) -> None:
    region, box = region_with_box

    assert coupled_with_region(box, box_to_contour(box),
                               context=context)
    assert coupled_with_region(from_contour(region,
                                            context=context),
                               region,
                               context=context)


@given(strategies.regions_with_boxes)
def test_equivalents(context: Context,
                     region_with_box: Tuple[Region, Box]) -> None:
    region, box = region_with_box

    result = coupled_with_region(box, region,
                                 context=context)

    box_vertices = box_to_contour(box)
    relation = region_in_region(box_vertices, region)
    assert equivalence(result,
                       relation in (Relation.OVERLAP,
                                    Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.EQUAL,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN)
                       or relation is Relation.TOUCH
                       and (contour_in_contour(box_vertices, region)
                            is Relation.OVERLAP))
    assert equivalence(result,
                       coupled_with_polygon(box, contour_to_polygon(region),
                                            context=context))
