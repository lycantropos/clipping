import math
from functools import partial
from operator import is_not
from typing import (List,
                    Optional,
                    Tuple)

from wagyu.hints import (Coordinate,
                         Point)
from .active_bounds import (insert_bounds,
                            update_current_x)
from .bound import (Bound,
                    intersection_compare)
from .bubble_sort import bubble_sort
from .local_minimum import (LocalMinimum,
                            to_scanbeams)
from .point import round_point
from .utils import (insort_unique,
                    quicksort,
                    round_half_up,
                    to_unique_just_seen)


def process_intersections(hot_pixels: List[Point],
                          top_y: Coordinate,
                          active_bounds: List[Bound]) -> List[Bound]:
    update_current_x(active_bounds, top_y)
    return bubble_sort(active_bounds, intersection_compare,
                       partial(on_bounds_swap, hot_pixels))


def on_bounds_swap(hot_pixels: List[Point],
                   first_bound: Bound,
                   second_bound: Bound) -> None:
    intersection = first_bound.current_edge & second_bound.current_edge
    if intersection is None:
        raise RuntimeError('Trying to find intersection of lines '
                           'that do not intersect')
    hot_pixels.append(round_point(intersection))


def process_local_minimum(hot_pixels: List[Point],
                          top_y: Coordinate,
                          minimums: List[LocalMinimum],
                          minimum_index: int,
                          active_bounds: List[Bound],
                          scanbeams: List[Coordinate]) -> int:
    while minimum_index < len(minimums) and minimums[minimum_index].y == top_y:
        minimum = minimums[minimum_index]
        left_bound, right_bound = minimum.left_bound, minimum.right_bound
        hot_pixels.append(left_bound.edges[0].bottom)

        left_bound.current_edge_index = 0
        left_bound.next_edge_index = 1
        left_bound.current_x = left_bound.current_edge.bottom_x

        right_bound.current_edge_index = 0
        right_bound.next_edge_index = 1
        right_bound.current_x = right_bound.current_edge.bottom_x

        left_bound_index = insert_bounds(active_bounds, left_bound,
                                         right_bound)
        left_bound_current_edge = active_bounds[left_bound_index].current_edge
        if not left_bound_current_edge.is_horizontal:
            insort_unique(scanbeams, left_bound_current_edge.top_y)
        right_bound_index = left_bound_index + 1
        right_bound_current_edge = (active_bounds[right_bound_index]
                                    .current_edge)
        if not right_bound_current_edge.is_horizontal:
            insort_unique(scanbeams, right_bound_current_edge.top_y)
        minimum_index += 1
    return minimum_index


def process_bounds_at_top_of_scanbeam(hot_pixels: List[Point],
                                      top_y: Coordinate,
                                      scanbeams: List[Coordinate],
                                      active_bounds: List[Bound]
                                      ) -> List[Bound]:
    active_bounds = list(active_bounds)
    index = 0
    while index < len(active_bounds):
        bound = active_bounds[index]
        if bound is None:
            index += 1
            continue
        shifted = False
        current_index = index
        while (bound.current_edge_index < len(bound.edges)
               and bound.current_edge.top_y == top_y):
            current_edge = bound.current_edge
            hot_pixels.append(current_edge.top)
            if current_edge.is_horizontal:
                current_index, shifted = process_bound_at_top_of_scanbeam(
                        hot_pixels, top_y, active_bounds, current_index)
            bound.to_next_edge(scanbeams)
        if bound.current_edge_index == len(bound.edges):
            active_bounds[current_index] = None
        if not shifted:
            index += 1
    return list(filter(partial(is_not, None), active_bounds))


def process_bound_at_top_of_scanbeam(hot_pixels: List[Point],
                                     top_y: Coordinate,
                                     active_bounds: List[Bound],
                                     bound_index: int) -> Tuple[int, bool]:
    shifted = False
    bound = active_bounds[bound_index]
    current_edge = bound.current_edge
    bound.current_x = current_edge.top_x
    if current_edge.bottom_x < current_edge.top_x:
        for next_bound_index in range(bound_index + 1, len(active_bounds)):
            next_bound = active_bounds[next_bound_index]
            if (next_bound is not None
                    and next_bound.current_x >= bound.current_x):
                break
            if (next_bound is not None
                    and next_bound.current_edge.top_y != top_y
                    and next_bound.current_edge.bottom_y != top_y):
                hot_pixels.append((round_half_up(next_bound.current_x), top_y))
            active_bounds[bound_index], active_bounds[next_bound_index] = (
                next_bound, bound)
            bound_index = next_bound_index
            if not shifted:
                shifted = True
    else:
        for prev_bound_index in range(bound_index - 1, -1, -1):
            prev_bound = active_bounds[prev_bound_index]
            if (prev_bound is not None
                    and prev_bound.current_x <= bound.current_x):
                break
            if (prev_bound is not None
                    and prev_bound.current_edge.top_y != top_y
                    and prev_bound.current_edge.bottom_y != top_y):
                hot_pixels.append((round_half_up(prev_bound.current_x), top_y))
            active_bounds[bound_index], active_bounds[prev_bound_index] = (
                prev_bound, bound)
            bound_index = prev_bound_index
    return bound_index, shifted


def from_local_minimums(minimums: List[LocalMinimum]) -> List[Point]:
    minimums = sorted(minimums,
                      reverse=True)
    minimum_index = 0
    scanbeams = to_scanbeams(minimums)
    active_bounds = []  # type: List[Optional[Bound]]
    scanline_y = math.inf
    result = []  # type: List[Point]
    while scanbeams or minimum_index < len(minimums):
        try:
            scanline_y = scanbeams.pop()
        except IndexError:
            pass
        active_bounds = process_intersections(result, scanline_y,
                                              active_bounds)
        minimum_index = process_local_minimum(result, scanline_y, minimums,
                                              minimum_index, active_bounds,
                                              scanbeams)
        active_bounds = process_bounds_at_top_of_scanbeam(
                result, scanline_y, scanbeams, active_bounds)
    quicksort(result, compare)
    return to_unique_just_seen(result)


def compare(left: Point, right: Point) -> bool:
    left_x, left_y = left
    right_x, right_y = right
    return (right_y, left_x) >= (left_y, right_x)
