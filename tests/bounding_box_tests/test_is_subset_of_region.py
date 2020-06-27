from typing import Tuple

from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding_box import (is_subset_of_region,
                                        to_vertices)
from clipping.core.hints import BoundingBox
from clipping.hints import Contour
from . import strategies


@given(strategies.contours_with_bounding_boxes)
def test_basic(contour_with_bounding_box: Tuple[Contour, BoundingBox]) -> None:
    contour, bounding_box = contour_with_bounding_box

    result = is_subset_of_region(bounding_box, contour)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_self(bounding_box: BoundingBox) -> None:
    assert is_subset_of_region(bounding_box, list(to_vertices(bounding_box)))


@given(strategies.contours_with_bounding_boxes)
def test_equivalents(contour_with_bounding_box: Tuple[Contour, BoundingBox]
                     ) -> None:
    contour, bounding_box = contour_with_bounding_box

    result = is_subset_of_region(bounding_box, contour)

    assert result is (region_in_region(to_vertices(bounding_box), contour)
                      in (Relation.EQUAL,
                          Relation.ENCLOSED,
                          Relation.WITHIN))
