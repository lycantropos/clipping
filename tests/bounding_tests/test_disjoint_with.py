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

    result = disjoint_with(left_box, right_box)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_irreflexivity(box: Box) -> None:
    assert not disjoint_with(box, box)


@given(strategies.boxes_pairs)
def test_symmetry(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    assert (disjoint_with(left_box, right_box)
            is disjoint_with(right_box, left_box))


@given(strategies.boxes_pairs)
def test_equivalents(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = disjoint_with(left_box, right_box)

    assert result is not intersects_with(left_box, right_box)
    assert result is not (touches_with(left_box, right_box)
                          or coupled_with(left_box, right_box))
    assert result is (region_in_region(box_to_contour(left_box),
                                       box_to_contour(right_box))
                      is Relation.DISJOINT)
