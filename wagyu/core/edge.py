import math
from typing import Optional

from reprit.base import generate_repr

from wagyu.hints import (Coordinate,
                         Point)
from .utils import (round_towards_max,
                    round_towards_min)


class Edge:
    __slots__ = 'top_x', 'top_y', 'bottom_x', 'bottom_y', 'slope'

    def __init__(self, bottom: Point, top: Point) -> None:
        _, bottom_y = bottom
        _, top_y = top
        (self.bottom_x, self.bottom_y), (self.top_x, self.top_y) = (
            (top, bottom) if bottom_y < top_y else (bottom, top))
        dy = self.top_y - self.bottom_y
        self.slope = (self.top_x - self.bottom_x) / dy if dy else math.inf

    @property
    def bottom(self) -> Point:
        return self.bottom_x, self.bottom_y

    @property
    def top(self) -> Point:
        return self.top_x, self.top_y

    __repr__ = generate_repr(__init__)

    def __and__(self, other: 'Edge') -> Optional[Point]:
        delta_x = self.top_x - self.bottom_x
        delta_y = self.top_y - self.bottom_y
        other_delta_x = other.top_x - other.bottom_x
        other_delta_y = other.top_y - other.bottom_y
        denominator = delta_x * other_delta_y - other_delta_x * delta_y
        if not denominator:
            return None
        s = ((-delta_y * (self.bottom_x - other.bottom_x)
              + delta_x * (self.bottom_y - other.bottom_y))
             / denominator)
        t = ((other_delta_x * (self.bottom_y - other.bottom_y)
              - other_delta_y * (self.bottom_x - other.bottom_x))
             / denominator)
        return ((self.bottom_x + (t * delta_x),
                 self.bottom_y + (t * delta_y))
                if 0. <= s <= 1. and 0. <= t <= 1.
                else None)

    def __eq__(self, other: 'Edge') -> bool:
        return (self.top == other.top and self.bottom == other.bottom
                if isinstance(other, Edge)
                else NotImplemented)

    @property
    def is_horizontal(self) -> bool:
        return math.isinf(self.slope)

    def get_current_x(self, current_y: Coordinate) -> Coordinate:
        return float(
                self.top_x
                if current_y == self.top_y
                else self.bottom_x + self.slope * (current_y - self.bottom_y))

    def get_min_x(self, current_y: Coordinate) -> Coordinate:
        if self.is_horizontal:
            return min(self.bottom_x, self.top_x)
        elif self.slope > 0:
            if current_y == self.top_y:
                return self.top_x
            else:
                lower_range_y = current_y - self.bottom_y - 0.5
                return round_towards_min(self.bottom_x
                                         + self.slope * lower_range_y)
        elif current_y == self.bottom_y:
            return self.bottom_x
        else:
            lower_range_y = current_y - self.bottom_y + 0.5
            return round_towards_min(self.bottom_x
                                     + self.slope * lower_range_y)

    def get_max_x(self, current_y: Coordinate) -> Coordinate:
        if self.is_horizontal:
            return max(self.bottom_x, self.top_x)
        elif self.slope < 0:
            if current_y == self.top_y:
                return self.top_x
            else:
                lower_range_y = current_y - self.bottom_y - 0.5
                return round_towards_max(self.bottom_x
                                         + self.slope * lower_range_y)
        elif current_y == self.bottom_y:
            return self.bottom_x
        else:
            lower_range_y = current_y - self.bottom_y + 0.5
            return round_towards_max(self.bottom_x
                                     + self.slope * lower_range_y)

    def reverse_horizontal(self) -> None:
        self.top_x, self.bottom_x = self.bottom_x, self.top_x


def are_edges_slopes_equal(first: Edge, second: Edge) -> bool:
    return ((first.top_y - first.bottom_y) * (second.top_x - second.bottom_x)
            == ((first.top_x - first.bottom_x)
                * (second.top_y - second.bottom_y)))
