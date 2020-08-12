from functools import partial
from typing import List

from wagyu.core.bound import Bound
from wagyu.core.enums import Fill
from wagyu.core.utils import (are_floats_almost_equal,
                              are_floats_greater_than,
                              are_floats_less_than,
                              find_if)
from wagyu.hints import Coordinate


def insert_bounds(active_bounds: List[Bound],
                  left: Bound,
                  right: Bound) -> int:
    index = find_if(partial(is_bound_insert_location, left), active_bounds)
    active_bounds.insert(index, right)
    active_bounds.insert(index, left)
    return index


def is_bound_insert_location(left: Bound, right: Bound) -> bool:
    if are_floats_almost_equal(left.current_x, right.current_x):
        if left.current_edge.top_y > right.current_edge.top_y:
            return are_floats_less_than(float(left.current_edge.top_x),
                                        right.current_edge.get_current_x(
                                                left.current_edge.top_y))
        else:
            return are_floats_greater_than(float(right.current_edge.top_x),
                                           left.current_edge.get_current_x(
                                                   right.current_edge.top_y))
    else:
        return left.current_x < right.current_x


def set_winding_count(active_bounds: List[Bound],
                      bound_index: int,
                      subject_fill: Fill,
                      clip_fill: Fill) -> None:
    bound = active_bounds[bound_index]
    if not bound_index:
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = 0
        return
    prev_bound_index = to_prev_same_operand_kind_bound_index(active_bounds,
                                                             bound_index)
    if prev_bound_index == -1:
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = 0
    elif bound.is_even_odd_fill(subject_fill, clip_fill):
        # even-odd filling
        bound.winding_count = bound.winding_delta
        bound.opposite_winding_count = (active_bounds[prev_bound_index]
                                        .opposite_winding_count)
    else:
        # non-zero, positive or negative filling
        reversed_bound = active_bounds[prev_bound_index]
        if reversed_bound.winding_count * reversed_bound.winding_delta < 0:
            # previous edge is 'decreasing' winding count toward zero
            # so we're outside the previous polygon
            if abs(reversed_bound.winding_count) > 1:
                # outside previous polygon but still inside another,
                # when reversing direction of previous polygon
                # use the same winding count
                if reversed_bound.winding_delta * bound.winding_delta < 0:
                    bound.winding_count = reversed_bound.winding_count
                else:
                    # otherwise continue to 'decrease' winding count
                    bound.winding_count = (reversed_bound.winding_count
                                           + bound.winding_delta)
            else:
                # now outside all polygons of same polygon kind
                # so set own winding count
                bound.winding_count = bound.winding_delta
        else:
            # previous edge is 'increasing' winding count away from zero
            # so we're inside the previous polygon
            if reversed_bound.winding_delta * bound.winding_delta < 0:
                # if wind direction is reversing previous
                # then use same winding count
                bound.winding_count = reversed_bound.winding_count
            else:
                # otherwise add to winding count
                bound.winding_count = (reversed_bound.winding_count
                                       + bound.winding_delta)
        bound.opposite_winding_count = reversed_bound.opposite_winding_count
    # update opposite winding count
    forward_bound_index = prev_bound_index + 1
    if bound.is_even_odd_other_fill(subject_fill, clip_fill):
        # even-odd filling
        for forward_bound_index in range(forward_bound_index, bound_index):
            bound.opposite_winding_count = int(
                    not bound.opposite_winding_count)
    else:
        # non-zero, positive or negative filling
        for forward_bound_index in range(forward_bound_index, bound_index):
            bound.opposite_winding_count += (active_bounds[forward_bound_index]
                                             .winding_delta)


def to_prev_same_operand_kind_bound_index(active_bounds: List[Bound],
                                          bound_index: int) -> int:
    bound = active_bounds[bound_index]
    result = bound_index - 1
    while (result >= 0
           and active_bounds[result].operand_kind is not bound.operand_kind):
        result -= 1
    return result


def update_current_x(active_bounds: List[Bound], top_y: Coordinate) -> None:
    for position, bound in enumerate(active_bounds):
        bound.position = position
        bound.current_x = bound.current_edge.get_current_x(top_y)
