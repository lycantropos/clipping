from typing import Iterable

from robust.linear import (SegmentsRelationship,
                           segments_relationship)

from clipping.core.utils import flatten
from clipping.hints import (BoundingBox,
                            Multisegment,
                            Point,
                            Segment)


def from_points(points: Iterable[Point]) -> BoundingBox:
    """
    Builds bounding box from points.
    """
    points = iter(points)
    x_min, y_min = x_max, y_max = next(points)
    for x, y in points:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def from_multisegment(multisegment: Multisegment) -> BoundingBox:
    """
    Builds bounding box from multisegment.
    """
    return from_points(flatten(multisegment))


def disjoint_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes do not intersect.
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min)


def intersects_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect.
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (right_x_min <= left_x_max and left_x_min <= right_x_max
            and right_y_min <= left_y_max and left_y_min <= right_y_max)


def overlaps_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect in some region.
    """
    return intersects_with(left, right) and not touches_with(left, right)


def touches_with(left: BoundingBox, right: BoundingBox) -> bool:
    """
    Checks if bounding boxes intersect at point or by the edge.
    """
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return ((left_x_min == right_x_max or left_x_max == right_x_min)
            and (left_y_min == right_y_max or left_y_max == right_y_min))


def is_subset_of(test: BoundingBox, goal: BoundingBox) -> bool:
    """
    Checks if the bounding box is the subset of the other.
    """
    test_x_min, test_x_max, test_y_min, test_y_max = test
    goal_x_min, goal_x_max, goal_y_min, goal_y_max = goal
    return (goal_x_min <= test_x_min and test_x_max <= goal_x_max
            and goal_y_min <= test_y_min and test_y_max <= goal_y_max)


def intersects_with_segment(bounding_box: BoundingBox,
                            segment: Segment) -> bool:
    """
    Checks if the bounding box intersects the segment.
    """
    segment_bounding_box = from_points(segment)
    return (intersects_with(segment_bounding_box, bounding_box)
            and (is_subset_of(segment_bounding_box, bounding_box)
                 or any(segments_relationship(edge, segment)
                        is not SegmentsRelationship.NONE
                        for edge in to_segments(bounding_box))))


def overlaps_with_segment(bounding_box: BoundingBox,
                          segment: Segment) -> bool:
    """
    Checks if the bounding box intersects the segment at more than one point.
    """
    segment_bounding_box = from_points(segment)
    return (intersects_with(segment_bounding_box, bounding_box)
            and (is_subset_of(segment_bounding_box, bounding_box)
                 or any(segments_relationship(edge, segment)
                        not in (SegmentsRelationship.TOUCH,
                                SegmentsRelationship.NONE)
                        for edge in to_segments(bounding_box))))


def to_segments(bounding_box: BoundingBox) -> Iterable[Segment]:
    x_min, x_max, y_min, y_max = bounding_box
    return [((x_min, y_min), (x_max, y_min)),
            ((x_max, y_min), (x_max, y_max)),
            ((x_min, y_max), (x_max, y_max)),
            ((x_min, y_min), (x_min, y_max))]


def to_intersecting_segments(bounding_box: BoundingBox,
                             multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if intersects_with_segment(bounding_box, segment)]


def to_overlapping_segments(bounding_box: BoundingBox,
                            multisegment: Multisegment) -> Multisegment:
    return [segment
            for segment in multisegment
            if overlaps_with_segment(bounding_box, segment)]
