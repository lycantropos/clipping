from typing import Tuple

from ground.base import Context
from ground.hints import (Box,
                          Contour)
from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding import within_of_region
from tests.utils import box_to_contour
from . import strategies


@given(strategies.contours_with_boxes)
def test_basic(context: Context,
               contour_with_box: Tuple[Contour, Box]) -> None:
    contour, box = contour_with_box

    result = within_of_region(box, contour,
                              context=context)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_self(context: Context,
              box: Box) -> None:
    assert not within_of_region(box, box_to_contour(box),
                                context=context)


@given(strategies.contours_with_boxes)
def test_equivalents(context: Context,
                     contour_with_box: Tuple[Contour, Box]) -> None:
    contour, box = contour_with_box

    result = within_of_region(box, contour,
                              context=context)

    assert result is (region_in_region(box_to_contour(box), contour)
                      is Relation.WITHIN)
