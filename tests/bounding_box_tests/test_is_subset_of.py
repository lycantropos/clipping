from hypothesis import given
from orient.planar import (Relation,
                           region_in_region)

from clipping.core.bounding_box import (is_subset_of,
                                        to_vertices)
from clipping.core.hints import BoundingBox
from tests.utils import (BoundingBoxesPair,
                         BoundingBoxesTriplet,
                         implication)
from . import strategies


@given(strategies.bounding_boxes_pairs)
def test_basic(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = is_subset_of(left_bounding_box, right_bounding_box)

    assert isinstance(result, bool)


@given(strategies.bounding_boxes)
def test_reflexivity(bounding_box: BoundingBox) -> None:
    assert is_subset_of(bounding_box, bounding_box)


@given(strategies.bounding_boxes_pairs)
def test_antisymmetry(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    assert implication(is_subset_of(left_bounding_box, right_bounding_box)
                       and is_subset_of(right_bounding_box, left_bounding_box),
                       left_bounding_box == right_bounding_box)


@given(strategies.bounding_boxes_triplets)
def test_transitivity(bounding_boxes_triplet: BoundingBoxesTriplet) -> None:
    (left_bounding_box, mid_bounding_box,
     right_bounding_box) = bounding_boxes_triplet

    assert implication(is_subset_of(left_bounding_box, mid_bounding_box)
                       and is_subset_of(mid_bounding_box, right_bounding_box),
                       is_subset_of(left_bounding_box, right_bounding_box))


@given(strategies.bounding_boxes_pairs)
def test_equivalents(bounding_boxes_pair: BoundingBoxesPair) -> None:
    left_bounding_box, right_bounding_box = bounding_boxes_pair

    result = is_subset_of(left_bounding_box, right_bounding_box)

    assert result is (region_in_region(to_vertices(left_bounding_box),
                                       to_vertices(right_bounding_box))
                      in (Relation.EQUAL,
                          Relation.ENCLOSED,
                          Relation.WITHIN))
