from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding_box import (to_vertices,
                                        within_of)
from clipping.core.hints import BoundingBox
from tests.utils import (BoundingBoxesPair,
                         BoundingBoxesTriplet,
                         implication)
from . import strategies


@given(strategies.bounding_boxes_pairs)
def test_basic(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = within_of(left_bounding_box, right_bounding_box)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_irreflexivity(bounding_box: BoundingBox) -> None:
    assert not within_of(bounding_box, bounding_box)


@given(strategies.bounding_boxes_triplets)
def test_transitivity(bounding_boxes_triplet: BoundingBoxesTriplet) -> None:
    (left_bounding_box, mid_bounding_box,
     right_bounding_box) = bounding_boxes_triplet

    assert implication(within_of(left_bounding_box, mid_bounding_box)
                       and within_of(mid_bounding_box, right_bounding_box),
                       within_of(left_bounding_box, right_bounding_box))


@given(strategies.bounding_boxes_pairs)
def test_equivalents(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = within_of(left_bounding_box, right_bounding_box)

    assert result is (region_in_region(to_vertices(left_bounding_box),
                                       to_vertices(right_bounding_box))
                      is Relation.WITHIN)
