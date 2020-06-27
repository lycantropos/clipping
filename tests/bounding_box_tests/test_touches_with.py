from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding_box import (to_vertices,
                                        touches_with)
from clipping.core.hints import BoundingBox
from tests.utils import BoundingBoxesPair
from . import strategies


@given(strategies.bounding_boxes_pairs)
def test_basic(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = touches_with(left_bounding_box, right_bounding_box)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_irreflexivity(bounding_box: BoundingBox) -> None:
    assert not touches_with(bounding_box, bounding_box)


@given(strategies.bounding_boxes_pairs)
def test_symmetry(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    assert (touches_with(left_bounding_box, right_bounding_box)
            is touches_with(right_bounding_box, left_bounding_box))


@given(strategies.bounding_boxes_pairs)
def test_equivalents(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = touches_with(left_bounding_box, right_bounding_box)

    assert result is (region_in_region(to_vertices(left_bounding_box),
                                       to_vertices(right_bounding_box))
                      is Relation.TOUCH)
