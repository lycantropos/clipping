from typing import Tuple

from ground.base import Context
from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding import is_subset_of_region
from clipping.hints import Region
from . import strategies
from ..utils import box_to_contour


@given(strategies.contours_with_boxes)
def test_basic(context: Context, region_with_box: Tuple[Region, Box]) -> None:
    contour, box = region_with_box

    result = is_subset_of_region(box, contour,
                                 context=context)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_self(context: Context, box: Box) -> None:
    assert is_subset_of_region(box, box_to_contour(box),
                               context=context)


@given(strategies.contours_with_boxes)
def test_equivalents(context: Context,
                     contour_with_box: Tuple[Region, Box]) -> None:
    contour, box = contour_with_box

    result = is_subset_of_region(box, contour,
                                 context=context)

    assert result is (region_in_region(box_to_contour(box), contour)
                      in (Relation.EQUAL, Relation.ENCLOSED, Relation.WITHIN))
