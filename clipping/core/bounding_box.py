from typing import Iterable

from clipping.hints import (BoundingBox,
                            Point)


def from_points(points: Iterable[Point]) -> BoundingBox:
    points = iter(points)
    x_min, y_min = x_max, y_max = next(points)
    for x, y in points:
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def disjoint_with(left: BoundingBox, right: BoundingBox) -> bool:
    left_x_min, left_x_max, left_y_min, left_y_max = left
    right_x_min, right_x_max, right_y_min, right_y_max = right
    return (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min)
