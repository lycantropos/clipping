from fractions import Fraction
from itertools import chain
from typing import (Iterable,
                    List,
                    Tuple,
                    Type,
                    Union)

from bentley_ottmann import linear
from bentley_ottmann.angular import (Orientation,
                                     to_orientation as to_real_orientation)

from .hints import (Base,
                    BoundingBox,
                    Contour,
                    Coordinate,
                    Multipolygon,
                    Point,
                    Segment)


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for border, holes in multipolygon:
        yield border
        yield from holes


def to_bounding_box(multipolygon: Multipolygon) -> BoundingBox:
    ((first_vertex, *rest_vertices), _), *rest_polygons = multipolygon
    x_min, y_min = x_max, y_max = first_vertex
    for x, y in chain.from_iterable([rest_vertices]
                                    + [border for border, _ in rest_polygons]):
        x_min, x_max = min(x_min, x), max(x_max, x)
        y_min, y_max = min(y_min, y), max(y_max, y)
    return x_min, x_max, y_min, y_max


def to_segments(contour: Contour) -> List[Segment]:
    return [(contour[index], contour[(index + 1) % len(contour)])
            for index in range(len(contour))]


def to_multipolygon_base(multipolygon: Multipolygon) -> Base:
    first_left_polygon_border, _ = multipolygon[0]
    return to_contour_base(first_left_polygon_border)


def to_contour_base(contour: Contour) -> Base:
    first_vertex_x, _ = contour[0]
    return type(first_vertex_x)


def to_non_real_orientation(first_ray_point: Point,
                            vertex: Point,
                            second_ray_point: Point) -> Orientation:
    return to_real_orientation(_to_real_point(first_ray_point),
                               _to_real_point(vertex),
                               _to_real_point(second_ray_point))


to_rational_intersections = linear.find_intersections


def to_irrational_intersections(first_segment: Segment,
                                second_segment: Segment
                                ) -> Union[Tuple[()], Tuple[Point],
                                           Tuple[Point, Point]]:
    return to_rational_intersections(to_rational_segment(first_segment),
                                     to_rational_segment(second_segment))


def to_non_real_intersections(base: Type[Coordinate],
                              first_segment: Segment,
                              second_segment: Segment
                              ) -> Union[Tuple[()], Tuple[Point],
                                         Tuple[Point, Point]]:
    result = to_irrational_intersections(first_segment, second_segment)
    return tuple(point_to_irrational_base(base, point) for point in result)


def to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_rational_point(start), to_rational_point(end)


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)


def point_to_irrational_base(base: Type[Coordinate], point: Point) -> Point:
    x, y = point
    return (base(x.numerator) / x.denominator,
            base(y.numerator) / y.denominator)


def _to_real_point(point: Point) -> Point:
    x, y = point
    return float(x), float(y)
