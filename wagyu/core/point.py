from wagyu.hints import Point
from .utils import round_towards_max


def round_point(point: Point) -> Point:
    x, y = point
    return round_towards_max(x), round_towards_max(y)


def are_points_slopes_equal(first: Point, second: Point, third: Point) -> bool:
    first_x, first_y = first
    second_x, second_y = second
    third_x, third_y = third
    return ((first_y - second_y) * (second_x - third_x)
            == (first_x - second_x) * (second_y - third_y))


def is_point_between_others(pt1: Point, pt2: Point, pt3: Point) -> bool:
    if pt1 == pt2 or pt2 == pt3 or pt1 == pt3:
        return False
    pt1_x, pt1_y = pt1
    pt2_x, pt2_y = pt2
    pt3_x, pt3_y = pt3
    if pt1_x != pt3_x:
        return (pt2_x > pt1_x) is (pt2_x < pt3_x)
    else:
        return (pt2_y > pt1_y) is (pt2_y < pt3_y)
