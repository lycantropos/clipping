from typing import Tuple

from wagyu.hints import Coordinate

BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]


def is_subset_of(test: BoundingBox, goal: BoundingBox) -> bool:
    """
    Checks if the bounding box is the subset of the other.

    >>> is_subset_of((0, 2, 0, 2), (0, 2, 0, 2))
    True
    >>> is_subset_of((0, 2, 0, 2), (1, 3, 1, 3))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 0, 2))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 2, 4))
    False
    >>> is_subset_of((0, 2, 0, 2), (2, 4, 3, 5))
    False
    """
    test_x_min, test_x_max, test_y_min, test_y_max = test
    goal_x_min, goal_x_max, goal_y_min, goal_y_max = goal
    return (goal_x_min <= test_x_min and test_x_max <= goal_x_max
            and goal_y_min <= test_y_min and test_y_max <= goal_y_max)
