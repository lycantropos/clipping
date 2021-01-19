from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding import touches_with
from tests.utils import (BoxesPair,
                         box_to_contour)
from . import strategies


@given(strategies.boxes_pairs)
def test_basic(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = touches_with(left_box, right_box)

    assert isinstance(result, bool)


@given(strategies.non_degenerate_boxes)
def test_irreflexivity(box: Box) -> None:
    assert not touches_with(box, box)


@given(strategies.boxes_pairs)
def test_symmetry(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    assert (touches_with(left_box, right_box)
            is touches_with(right_box, left_box))


@given(strategies.boxes_pairs)
def test_equivalents(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = touches_with(left_box, right_box)

    assert result is (region_in_region(box_to_contour(left_box),
                                       box_to_contour(right_box))
                      is Relation.TOUCH)
