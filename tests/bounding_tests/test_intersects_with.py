from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding import (coupled_with,
                                    disjoint_with,
                                    intersects_with,
                                    touches_with)
from tests.utils import (BoxesPair,
                         box_to_contour)
from . import strategies


@given(strategies.boxes_pairs)
def test_basic(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = intersects_with(left_box, right_box)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_reflexivity(box: Box) -> None:
    assert intersects_with(box, box)


@given(strategies.boxes_pairs)
def test_symmetry(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    assert (intersects_with(left_box, right_box)
            is intersects_with(right_box, left_box))


@given(strategies.boxes_pairs)
def test_equivalents(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = intersects_with(left_box, right_box)

    assert result is not disjoint_with(left_box, right_box)
    assert result is (touches_with(left_box, right_box)
                      or coupled_with(left_box, right_box))
    assert result is (region_in_region(box_to_contour(left_box),
                                       box_to_contour(right_box))
                      is not Relation.DISJOINT)
