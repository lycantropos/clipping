from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding import within_of
from tests.utils import (BoxesPair,
                         BoxesTriplet,
                         box_to_contour,
                         implication)
from . import strategies


@given(strategies.boxes_pairs)
def test_basic(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = within_of(left_box, right_box)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_irreflexivity(box: Box) -> None:
    assert not within_of(box, box)


@given(strategies.boxes_triplets)
def test_transitivity(boxes_triplet: BoxesTriplet) -> None:
    (left_box, mid_box,
     right_box) = boxes_triplet

    assert implication(within_of(left_box, mid_box)
                       and within_of(mid_box, right_box),
                       within_of(left_box, right_box))


@given(strategies.boxes_pairs)
def test_equivalents(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = within_of(left_box, right_box)

    assert result is (region_in_region(box_to_contour(left_box),
                                       box_to_contour(right_box))
                      is Relation.WITHIN)
