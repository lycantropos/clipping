from ground.hints import Box
from hypothesis import given
from orient.planar import (Relation,
                           contour_in_contour,
                           region_in_region)

from clipping.core.bounding import coupled_with
from tests.utils import (BoxesPair,
                         box_to_contour,
                         equivalence)
from . import strategies


@given(strategies.boxes_pairs)
def test_basic(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = coupled_with(left_box, right_box)

    assert isinstance(result, bool)


@given(strategies.boxes)
def test_reflexivity(box: Box) -> None:
    assert coupled_with(box, box)


@given(strategies.boxes_pairs)
def test_symmetry(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    assert (coupled_with(left_box, right_box)
            is coupled_with(right_box, left_box))


@given(strategies.boxes_pairs)
def test_equivalents(boxes_pair: BoxesPair) -> None:
    left_box, right_box = boxes_pair

    result = coupled_with(left_box, right_box)

    left_box_contour = box_to_contour(left_box)
    right_box_contour = box_to_contour(right_box)
    relation = region_in_region(left_box_contour, right_box_contour)
    assert equivalence(result,
                       relation in (Relation.OVERLAP,
                                    Relation.COVER,
                                    Relation.ENCLOSES,
                                    Relation.EQUAL,
                                    Relation.ENCLOSED,
                                    Relation.WITHIN)
                       or relation is Relation.TOUCH
                       and (contour_in_contour(left_box_contour,
                                               right_box_contour)
                            is Relation.OVERLAP))
