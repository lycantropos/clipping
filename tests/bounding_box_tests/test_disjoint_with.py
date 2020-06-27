from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding_box import (coupled_with,
                                        disjoint_with,
                                        intersects_with,
                                        to_vertices,
                                        touches_with)
from clipping.core.hints import BoundingBox
from tests.utils import BoundingBoxesPair
from . import strategies


@given(strategies.bounding_boxes_pairs)
def test_basic(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = disjoint_with(left_bounding_box, right_bounding_box)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_irreflexivity(bounding_box: BoundingBox) -> None:
    assert not disjoint_with(bounding_box, bounding_box)


@given(strategies.bounding_boxes_pairs)
def test_symmetry(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    assert (disjoint_with(left_bounding_box, right_bounding_box)
            is disjoint_with(right_bounding_box, left_bounding_box))


@given(strategies.bounding_boxes_pairs)
def test_equivalents(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = disjoint_with(left_bounding_box, right_bounding_box)

    assert result is not intersects_with(left_bounding_box, right_bounding_box)
    assert result is not (touches_with(left_bounding_box, right_bounding_box)
                          or coupled_with(left_bounding_box,
                                          right_bounding_box))
    assert result is (region_in_region(to_vertices(left_bounding_box),
                                       to_vertices(right_bounding_box))
                      is Relation.DISJOINT)
