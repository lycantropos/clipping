import math
from collections import (defaultdict,
                         deque)
from functools import partial
from operator import is_not
from typing import (Dict,
                    List,
                    Optional,
                    Set,
                    Tuple)

from reprit.base import generate_repr

from wagyu.hints import (Coordinate,
                         Multipolygon,
                         Point)
from .active_bounds import (insert_bounds,
                            set_winding_count,
                            update_current_x)
from .bound import Bound
from .enums import (EdgeSide,
                    Fill,
                    OperandKind,
                    OperationKind)
from .intersect_node import (IntersectNode,
                             build_intersect_list)
from .local_minimum import (LocalMinimum,
                            to_scanbeams)
from .point import round_point
from .point_node import (PointNode,
                         find_start_and_end_of_collinear_edges,
                         fix_collinear_path,
                         has_collinear_edge)
from .polygon import rings_to_polygons
from .ring import (Ring,
                   remove_from_children,
                   set_to_children)
from .utils import (are_floats_greater_than,
                    are_floats_less_than,
                    find,
                    find_if,
                    insort_unique,
                    is_float_almost_zero,
                    is_odd,
                    round_half_up)

ConnectionMap = Dict[int, List[Tuple[PointNode, PointNode]]]


def ring_have_points_and_non_zero_area(ring: Ring) -> bool:
    return ring.node is not None and not is_float_almost_zero(ring.area)


class RingManager:
    __slots__ = ('children', 'all_nodes', 'hot_pixels',
                 '_current_hot_pixel_index', 'nodes', 'rings', 'index')

    def __init__(self,
                 children: Optional[List[Optional[Ring]]] = None,
                 hot_pixels: Optional[List[Point]] = None,
                 current_hot_pixel_index: Optional[int] = None,
                 rings: Optional[List[Ring]] = None,
                 index: int = 0) -> None:
        self.children = [] if children is None else children
        self.hot_pixels = [] if hot_pixels is None else hot_pixels
        self._current_hot_pixel_index = (
            None
            if (current_hot_pixel_index is None
                or current_hot_pixel_index >= len(self.hot_pixels))
            else current_hot_pixel_index)
        self.rings = [] if rings is None else rings
        self.index = index
        self.all_nodes = []  # type: List[Optional[PointNode]]
        self.nodes = []  # type: List[PointNode]

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'RingManager') -> bool:
        return (self.children == other.children
                and self.all_nodes == other.all_nodes
                and self.hot_pixels == other.hot_pixels
                and (self.current_hot_pixel_index
                     == other.current_hot_pixel_index)
                and self.nodes == other.nodes
                and self.rings == other.rings
                and self.index == other.index
                if isinstance(other, RingManager)
                else NotImplemented)

    @property
    def current_hot_pixel_index(self) -> int:
        return (len(self.hot_pixels)
                if (self._current_hot_pixel_index is None
                    or self._current_hot_pixel_index >= len(self.hot_pixels))
                else self._current_hot_pixel_index)

    @current_hot_pixel_index.setter
    def current_hot_pixel_index(self, value: int) -> None:
        self._current_hot_pixel_index = (value
                                         if value < len(self.hot_pixels)
                                         else None)

    def add_first_point(self, bound: Bound, active_bounds: List[Bound],
                        point: Point) -> None:
        ring = bound.ring = self.create_ring()
        ring.node = self.create_point_node(ring, point)
        self.set_hole_state(bound, active_bounds)
        bound.last_point = point

    def add_local_maximum_point(self,
                                point: Point,
                                first_bound: Bound,
                                second_bound: Bound,
                                active_bounds: List[Bound]) -> None:
        self.insert_hot_pixels_in_path(second_bound, point, False)
        self.add_point(first_bound, active_bounds, point)
        if first_bound.ring is second_bound.ring:
            first_bound.ring = None
            second_bound.ring = None
            # I am not certain that order is important here?
        elif first_bound.ring.index < second_bound.ring.index:
            self.append_ring(first_bound, second_bound, active_bounds)
        else:
            self.append_ring(second_bound, first_bound, active_bounds)

    def add_local_minimum_point(self,
                                point: Point,
                                first_bound: Bound,
                                second_bound: Bound,
                                active_bounds: List[Bound]) -> None:
        if (second_bound.current_edge.is_horizontal
                or (first_bound.current_edge.slope
                    > second_bound.current_edge.slope)):
            self.add_point(first_bound, active_bounds, point)
            second_bound.last_point = point
            second_bound.ring = first_bound.ring
            first_bound.side = EdgeSide.LEFT
            second_bound.side = EdgeSide.RIGHT
        else:
            self.add_point(second_bound, active_bounds, point)
            first_bound.last_point = point
            first_bound.ring = second_bound.ring
            first_bound.side = EdgeSide.RIGHT
            second_bound.side = EdgeSide.LEFT

    def add_point(self, bound: Bound, active_bounds: List[Bound],
                  point: Point) -> None:
        if bound.ring is None:
            self.add_first_point(bound, active_bounds, point)
        else:
            self.add_point_to_ring(bound, point)

    def add_point_to_ring(self, bound: Bound, point: Point) -> None:
        assert bound.ring is not None
        # handle hot pixels
        self.insert_hot_pixels_in_path(bound, point, False)
        # ``bound.ring.node`` is the 'leftmost' point,
        # ``bound.ring.node.prev`` is the 'rightmost'
        op = bound.ring.node
        to_front = bound.side is EdgeSide.LEFT
        if to_front and point == op or (not to_front and (point == op.prev)):
            return
        new_node = self.create_point_node(bound.ring, point, op)
        if to_front:
            bound.ring.node = new_node

    def append_ring(self, first_bound: Bound, second_bound: Bound,
                    active_bounds: List[Bound]) -> None:
        # get the start and ends of both output polygons
        first_out_rec = first_bound.ring
        second_out_rec = second_bound.ring
        if first_out_rec.is_descendant_of(second_out_rec):
            keep_ring, remove_ring = second_out_rec, first_out_rec
            keep_bound, remove_bound = second_bound, first_bound
        elif second_out_rec.is_descendant_of(first_out_rec):
            keep_ring, remove_ring = first_out_rec, second_out_rec
            keep_bound, remove_bound = first_bound, second_bound
        elif first_out_rec is first_out_rec.get_lowermost_ring(second_out_rec):
            keep_ring, remove_ring = first_out_rec, second_out_rec
            keep_bound, remove_bound = first_bound, second_bound
        else:
            keep_ring, remove_ring = second_out_rec, first_out_rec
            keep_bound, remove_bound = second_bound, first_bound
        # get the start and ends of both output polygons and
        # join second bound's polygon onto first bound's polygon
        # and delete pointers to second bound
        p1_lft = keep_ring.node
        p1_rt = p1_lft.prev
        p2_lft = remove_ring.node
        p2_rt = p2_lft.prev
        # join second bound's polygon onto first bound's polygon
        # and delete pointers to second bound
        if keep_bound.side is EdgeSide.LEFT:
            if remove_bound.side is EdgeSide.LEFT:
                # z y x a b c
                p2_lft.reverse()
                p2_lft.next = p1_lft
                p1_lft.prev = p2_lft
                p1_rt.next = p2_rt
                p2_rt.prev = p1_rt
                keep_ring.node = p2_rt
            else:
                # x y z a b c
                p2_rt.next = p1_lft
                p1_lft.prev = p2_rt
                p2_lft.prev = p1_rt
                p1_rt.next = p2_lft
                keep_ring.node = p2_lft
        else:
            if remove_bound.side is EdgeSide.RIGHT:
                # a b c z y x
                p2_lft.reverse()
                p1_rt.next = p2_rt
                p2_rt.prev = p1_rt
                p2_lft.next = p1_lft
                p1_lft.prev = p2_lft
            else:
                # a b c x y z
                p1_rt.next = p2_lft
                p2_lft.prev = p1_rt
                p1_lft.prev = p2_rt
                p2_rt.next = p1_lft
        keep_ring.bottom_node = None
        keep_is_hole = is_odd(keep_ring.depth)
        remove_is_hole = is_odd(remove_ring.depth)
        remove_ring.node = remove_ring.bottom_node = None
        if keep_is_hole is not remove_is_hole:
            self.replace_ring(remove_ring, keep_ring.parent)
        else:
            self.replace_ring(remove_ring, keep_ring)
        keep_ring.update_points()
        remove_bound.ring = keep_bound.ring = None
        for bound in active_bounds:
            if bound is None:
                continue
            if bound.ring is remove_ring:
                bound.ring = keep_ring
                bound.side = keep_bound.side
                # not sure why there is a break here but was transferred logic
                # from angus
                break

    def assign_as_child(self, new_ring: Ring, parent: Ring) -> None:
        # assigning as a child assumes that this is a brand new ring,
        # therefore it does not have any existing relationships
        if ((parent is None and new_ring.is_hole)
                or (parent is not None
                    and new_ring.is_hole is parent.is_hole)):
            raise RuntimeError('Trying to assign a child '
                               'that is the same orientation as the parent')
        children = self.children if parent is None else parent.children
        set_to_children(new_ring, children)
        new_ring.parent = parent

    def assign_as_sibling(self, new_ring: Ring, sibling: Ring) -> None:
        # assigning as a sibling assumes that this is a brand new ring,
        # therefore it does not have any existing relationships
        if new_ring.is_hole is not sibling.is_hole:
            raise RuntimeError('Trying to assign to be a sibling '
                               'that is not the same orientation '
                               'as the sibling')
        children = (self.children
                    if sibling.parent is None
                    else sibling.parent.children)
        set_to_children(new_ring, children)
        new_ring.parent = sibling.parent

    def assign_new_ring_parents(self,
                                original_ring: Ring,
                                new_rings: List[Ring]) -> List[Ring]:
        # first lets remove any rings that have zero area or have no points
        new_rings = list(filter(ring_have_points_and_non_zero_area, new_rings))
        if not new_rings:
            # no new rings created simply return;
            return new_rings
        # we should not have to re-assign the parent of the original ring
        # because we always maintained the largest ring
        # during splitting on repeated points
        original_ring_area = original_ring.area
        original_positive = original_ring_area > 0.

        # if there is only one new ring the logic is very simple
        # and we do not have to check which ring contains,
        # we only need to compare the areas of the original ring
        # and that of the new ring
        if len(new_rings) == 1:
            new_ring = new_rings[0]
            new_ring_area = new_ring.area
            new_positive = new_ring_area > 0.
            if original_positive is new_positive:
                # rings should be siblings
                self.assign_as_child(new_ring, original_ring.parent)
                self.reassign_children_if_necessary(new_ring, original_ring,
                                                    new_rings)
            else:
                self.assign_as_child(new_ring, original_ring)
                self.reassign_children_if_necessary(new_ring,
                                                    original_ring.parent,
                                                    new_rings)
            return new_rings
        # sort rings by absolute area in descending order
        # as we will assign the rings with the largest areas first
        new_rings = sorted(new_rings,
                           key=lambda ring: abs(ring.area),
                           reverse=True)
        for index, ring in enumerate(new_rings):
            new_ring_area = ring.area
            new_positive = new_ring_area > 0.
            same_orientation = new_positive is original_positive
            found = False
            # first lets check the trees of any new_rings
            # that might have been assigned as siblings to the original ring
            for prev_index in range(0, index):
                prev_ring = new_rings[prev_index]
                if prev_ring.parent is not original_ring.parent:
                    continue
                if same_orientation:
                    for prev_child in prev_ring.children:
                        if prev_child is None:
                            continue
                        if self.find_parent_in_tree(ring, prev_child):
                            self.reassign_children_if_necessary(
                                    ring, original_ring, new_rings)
                            found = True
                            break
                else:
                    if self.find_parent_in_tree(ring, prev_ring):
                        self.reassign_children_if_necessary(
                                ring, original_ring.parent, new_rings)
                        found = True
                if found:
                    break
            if found:
                continue
            if same_orientation:
                for original_child in original_ring.children:
                    if original_child is None:
                        continue
                    if self.find_parent_in_tree(ring, original_child):
                        self.reassign_children_if_necessary(
                                ring, original_ring, new_rings)
                        found = True
                        break
                if not found:
                    # if we didn't find any parent and the same orientation
                    # then it must be a sibling of the original ring
                    self.assign_as_child(ring, original_ring.parent)
                    self.reassign_children_if_necessary(ring, original_ring,
                                                        new_rings)
            else:
                if self.find_parent_in_tree(ring, original_ring):
                    self.reassign_children_if_necessary(
                            ring, original_ring.parent, new_rings)
                else:
                    raise RuntimeError('Unable to find a proper parent ring')
        return new_rings

    def build_result(self) -> Multipolygon:
        return list(rings_to_polygons(self.children))

    def correct_chained_repeats(self,
                                nodes: List[PointNode],
                                start: int,
                                stop: int,
                                connection_map: ConnectionMap) -> None:
        for index in range(start, stop):
            node = nodes[index]
            if node.ring is None:
                continue
            for next_index in range(index + 1, stop):
                next_node = nodes[next_index]
                if next_node.ring is None:
                    continue
                self.process_single_intersection(node, next_node,
                                                 connection_map)

    def correct_chained_rings(self) -> None:
        nodes = self.all_nodes
        if len(nodes) < 2:
            return
        # setup connection map which is a map of rings
        # and their connection point pairs with other rings
        connection_map = defaultdict(list)

        # now lets find and process any points that overlap,
        # we should have solved all situations
        # where these points would be self intersections of a ring
        # with earlier processing
        # so this should just be points where different rings are touching
        count = 0
        prev_index = 0
        index = 1
        while index < len(nodes):
            if nodes[prev_index] == nodes[index]:
                count += 1
                prev_index += 1
                index += 1
                if index < len(nodes):
                    continue
                else:
                    prev_index += 1
            else:
                prev_index += 1
                index += 1
            if count == 0:
                continue
            first_index = prev_index - (count + 1)
            self.correct_chained_repeats(nodes, first_index, prev_index,
                                         connection_map)
            count = 0

    def correct_collinear_edges(self) -> None:
        if len(self.all_nodes) < 2:
            return
        count = 0
        prev_index = 0
        index = 1
        while index < len(self.all_nodes):
            prev_node = self.all_nodes[prev_index]
            node = self.all_nodes[index]
            if prev_node == node:
                count += 1
                prev_index += 1
                index += 1
                if index < len(self.all_nodes):
                    continue
                else:
                    prev_index += 1
            else:
                prev_index += 1
                index += 1
            if count == 0:
                continue
            first_index = prev_index - (count + 1)
            self.correct_collinear_repeats(self.all_nodes, first_index,
                                           prev_index)
            count = 0

    def correct_collinear_repeats(self,
                                  nodes: List[PointNode],
                                  start: int,
                                  stop: int) -> None:
        for index in range(start, stop):
            node = nodes[index]
            if node.ring is None:
                continue
            other_index = start
            while other_index < stop:
                if node.ring is None:
                    break
                other_node = nodes[other_index]
                if other_node.ring is None or node is other_node:
                    other_index += 1
                    continue
                if self.process_collinear_edges(node, other_node):
                    other_index = start
                else:
                    other_index += 1

    def correct_orientations(self) -> None:
        for ring in self.rings:
            if ring.node is None:
                continue
            ring.recalculate_stats()
            if ring.size < 3:
                self.remove_ring_and_points(ring, False)
                continue
            if is_odd(ring.depth) is not ring.is_hole:
                ring.node.reverse()
                ring.recalculate_stats()

    def correct_repeated_points(self,
                                new_rings: List[Ring],
                                nodes: List[PointNode],
                                start: int,
                                stop: int) -> None:
        for index in range(start, stop):
            node = nodes[index]
            if node.ring is None:
                continue
            for next_index in range(index + 1, stop):
                next_node = nodes[next_index]
                if next_node.ring is None:
                    continue
                new_ring = self.correct_self_intersection(node, next_node)
                if new_ring is not None:
                    new_rings.append(new_ring)

    def correct_ring_self_intersections(self,
                                        ring: Ring,
                                        correct_tree: bool) -> bool:
        if ring.corrected or ring.node is None:
            return False
        new_rings = []
        self.find_and_correct_repeated_points(ring, new_rings)
        if correct_tree:
            self.assign_new_ring_parents(ring, new_rings)
        ring.corrected = True
        return True

    def correct_self_intersection(self,
                                  first_node: PointNode,
                                  second_node: PointNode) -> Optional[Ring]:
        if first_node.ring is not second_node.ring:
            return None
        ring = first_node.ring
        # split the polygon into two
        third_node = first_node.prev
        fourth_node = second_node.prev
        first_node.prev = fourth_node
        fourth_node.next = first_node
        second_node.prev = third_node
        third_node.next = second_node
        result = self.create_ring()
        first_area, first_size, first_box = first_node.stats
        second_area, second_size, second_box = second_node.stats
        if abs(first_area) > abs(second_area):
            ring.node = first_node
            ring.set_stats(first_area, first_size, first_box)
            result.node = second_node
            result.set_stats(second_area, second_size, second_box)
        else:
            ring.node = second_node
            ring.set_stats(second_area, second_size, second_box)
            result.node = first_node
            result.set_stats(first_area, first_size, first_box)
        result.update_points()
        return result

    def correct_self_intersections(self, correct_tree: bool) -> bool:
        result = False
        for ring in sorted(self.rings):
            if self.correct_ring_self_intersections(ring, correct_tree):
                result = True
        return result

    def correct_topology(self) -> None:
        # sort all the points,
        # this will be used for the locating of chained rings
        # and the collinear edges and only needs to be done once
        self.all_nodes.sort()
        # Initially the orientations of the rings
        # could be incorrect, we need to adjust them
        self.correct_orientations()
        # We should only have to fix collinear edges once.
        # During this we also correct self intersections
        self.correct_collinear_edges()
        self.correct_self_intersections(False)
        self.correct_tree()
        fixed_intersections = True
        while fixed_intersections:
            self.correct_chained_rings()
            fixed_intersections = self.correct_self_intersections(True)

    def correct_tree(self) -> None:
        # it is possible that vatti resulted in some parent child
        # relationships that are not quite right,
        # therefore we need to just rebuild the entire tree of rings

        # first lets process the rings in order of size from largest
        # area to smallest, we know right away
        # that no smaller ring could ever contain a larger ring
        # so we can use this to our advantage as we iterate over the rings
        sorted_rings = sorted(self.rings,
                              reverse=True)
        for index, ring in enumerate(sorted_rings):
            if ring.node is None:
                continue
            if ring.size < 3 or is_float_almost_zero(ring.area):
                self.remove_ring_and_points(ring, False)
                continue
            ring.corrected = True
            found = False
            # search in reverse from the current iterator back to the beginning
            # to see if any of those rings might be its parent.
            for reverse_index in range(index - 1, -1, -1):
                # If orientations are not different, this can't be its parent.
                reverse_ring = sorted_rings[reverse_index]
                if ring.is_hole is reverse_ring.is_hole:
                    continue
                if ring.is_subset_of(reverse_ring):
                    self.reassign_as_child(ring, reverse_ring)
                    found = True
                    break
            if not found:
                if ring.is_hole:
                    raise RuntimeError('Could not properly place hole '
                                       'to a parent')
                else:
                    # Assign to base of tree by passing None
                    self.reassign_as_child(ring, None)

    def create_point_node(self, ring: Optional[Ring], point: Point,
                          before_this_point: Optional[PointNode] = None
                          ) -> PointNode:
        result = PointNode(*point)
        result.ring = ring
        if before_this_point is not None:
            result.place_before(before_this_point)
        self.nodes.append(result)
        self.all_nodes.append(result)
        return result

    def create_ring(self) -> Ring:
        result = Ring(self.index)
        self.index += 1
        self.rings.append(result)
        return result

    def do_maxima(self,
                  operation_kind: OperationKind,
                  subject_fill: Fill,
                  clip_fill: Fill,
                  bound_index: int,
                  maximum_bound_index: int,
                  active_bounds: List[Bound]) -> int:
        next_bound_index = bound_index + 1
        result = bound_index
        skipped = False
        while (next_bound_index < len(active_bounds)
               and next_bound_index != maximum_bound_index):
            if active_bounds[next_bound_index] is None:
                next_bound_index += 1
                continue
            skipped = True
            bound = active_bounds[bound_index]
            self.intersect_bounds(bound.current_edge.top, operation_kind,
                                  subject_fill, clip_fill, bound,
                                  active_bounds[next_bound_index],
                                  active_bounds)
            active_bounds[bound_index], active_bounds[next_bound_index] = (
                active_bounds[next_bound_index], active_bounds[bound_index])
            bound_index = next_bound_index
            next_bound_index += 1
        assert ((active_bounds[bound_index].ring is None)
                is (active_bounds[maximum_bound_index].ring is None))
        if active_bounds[bound_index].ring is not None:
            bound = active_bounds[bound_index]
            self.add_local_maximum_point(bound.current_edge.top, bound,
                                         active_bounds[maximum_bound_index],
                                         active_bounds)
        active_bounds[bound_index] = active_bounds[maximum_bound_index] = None
        return result + (not skipped)

    def execute_vatti(self,
                      minimums: List[LocalMinimum],
                      operation_kind: OperationKind,
                      subject_fill: Fill,
                      clip_fill: Fill) -> None:
        sorted_minimums = sorted(minimums,
                                 reverse=True)
        scanbeams = to_scanbeams(minimums)
        active_bounds = []  # type: List[Optional[Bound]]
        self.current_hot_pixel_index = 0
        minimums_index = 0
        scanline_y = math.inf
        while scanbeams or minimums_index < len(minimums):
            try:
                scanline_y = scanbeams.pop()
            except IndexError:
                pass
            self.process_intersections(scanline_y, operation_kind,
                                       subject_fill, clip_fill, active_bounds)
            self.update_current_hot_pixel_index(scanline_y)
            # first we process bounds that has already been added
            # to the active bound list -- if the active bound list is empty
            # local minima that are at this scanline_y and have
            # a horizontal edge at the local minima will be processed
            active_bounds, minimums_index = (
                self.process_edges_at_top_of_scanbeam(
                        operation_kind, subject_fill, clip_fill,
                        scanline_y, scanbeams, active_bounds, minimums_index,
                        sorted_minimums))
            # next we will add local minima bounds to the active bounds list
            # that are on the local minima queue at this current scanline_y
            minimums_index = self.insert_local_minima_into_abl(
                    operation_kind, subject_fill, clip_fill, scanline_y,
                    scanbeams, sorted_minimums, minimums_index, active_bounds)

    def find_and_correct_repeated_points(self, ring: Ring,
                                         new_rings: List[Ring]) -> None:
        sorted_nodes = ring.sorted_nodes
        count = 0
        prev_index = 0
        index = 1
        while index < len(sorted_nodes):
            if sorted_nodes[prev_index] == sorted_nodes[index]:
                count += 1
                prev_index += 1
                index += 1
                if index < len(sorted_nodes):
                    continue
                else:
                    prev_index += 1
            else:
                prev_index += 1
                index += 1
            if count == 0:
                continue
            first_index = prev_index - (count + 1)
            self.correct_repeated_points(new_rings, sorted_nodes, first_index,
                                         prev_index)
            count = 0

    def find_intersect_loop(self,
                            connection_map: ConnectionMap,
                            iList: deque,
                            ring_parent: Ring,
                            ring_origin: Ring,
                            ring_search: Ring,
                            visited: Set[int],
                            orig_pt: PointNode,
                            prev_pt: PointNode) -> bool:
        # Check for direct connection
        nodes_pairs = connection_map[id(ring_search)]
        nodes_pairs_indices_to_remove = set()
        for index, (op1, op2) in enumerate(nodes_pairs):
            it_ring1 = op1.ring
            it_ring2 = op2.ring
            if (it_ring1 is None or it_ring2 is None
                    or it_ring1 is not ring_search
                    or not it_ring1.is_hole and not it_ring2.is_hole):
                nodes_pairs_indices_to_remove.add(index)
                continue
            if (it_ring2 is ring_origin
                    and (ring_parent and it_ring2
                         or ring_parent is it_ring2.parent)
                    and prev_pt != op2 and orig_pt != op2):
                iList.appendleft((ring_search, (op1, op2)))
                return True
        if nodes_pairs_indices_to_remove:
            nodes_pairs[:] = [nodes_pair
                              for index, nodes_pair in enumerate(nodes_pairs)
                              if index not in nodes_pairs_indices_to_remove]
        nodes_pairs = connection_map[id(ring_search)]
        visited.add(id(ring_search))
        # Check for connection through chain of other intersections
        for op1, op2 in nodes_pairs:
            it_ring = op2.ring
            if (id(it_ring) in visited
                    or it_ring is None
                    or ring_parent is not it_ring
                    and ring_parent is not it_ring.parent
                    or is_float_almost_zero(it_ring.area)
                    or prev_pt == op2):
                continue
            if (self.find_intersect_loop(connection_map, iList, ring_parent,
                                         ring_origin, it_ring,
                                         visited, orig_pt, op2)):
                iList.appendleft((ring_search, (op1, op2)))
                return True
        return False

    def find_parent_in_tree(self, ring: Ring, possible_parent: Ring) -> bool:
        # before starting this we are assuming that possible parent
        # and ring have opposite signs of their areas

        # first we must search all grandchildren
        for child in possible_parent.children:
            if child is None:
                continue
            for grand_child in child.children:
                if grand_child is None:
                    continue
                if self.find_parent_in_tree(ring, grand_child):
                    return True
        if ring.is_subset_of(possible_parent):
            self.reassign_as_child(ring, possible_parent)
            return True
        return False

    def hot_pixel_set_left_to_right(self,
                                    y: Coordinate,
                                    start_x: Coordinate,
                                    end_x: Coordinate,
                                    bound: Bound,
                                    hot_pixel_start: int,
                                    hot_pixel_stop: int,
                                    add_end_point: bool) -> int:
        x_min = max(bound.current_edge.get_min_x(y), start_x)
        x_max = min(bound.current_edge.get_max_x(y), end_x)
        for hot_pixel_index in range(hot_pixel_start, hot_pixel_stop):
            hot_pixel = hot_pixel_x, _ = self.hot_pixels[hot_pixel_index]
            if hot_pixel_x < x_min:
                continue
            elif hot_pixel_x > x_max:
                break
            if not add_end_point and hot_pixel_x == end_x:
                continue
            op = bound.ring.node
            to_front = bound.side is EdgeSide.LEFT
            if to_front and hot_pixel == op:
                continue
            elif not to_front and hot_pixel == op.prev:
                continue
            new_node = self.create_point_node(bound.ring, hot_pixel, op)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_stop
        return hot_pixel_index

    def hot_pixel_set_right_to_left(self,
                                    y: Coordinate,
                                    start_x: Coordinate,
                                    end_x: Coordinate,
                                    bound: Bound,
                                    hot_pixel_start: int,
                                    hot_pixel_stop: int,
                                    add_end_point: bool) -> int:
        x_min = max(bound.current_edge.get_min_x(y), end_x)
        x_max = min(bound.current_edge.get_max_x(y), start_x)
        for hot_pixel_index in reversed(range(hot_pixel_start,
                                              hot_pixel_stop)):
            hot_pixel = hot_pixel_x, _ = self.hot_pixels[hot_pixel_index]
            if hot_pixel_x > x_max:
                continue
            elif hot_pixel_x < x_min:
                break
            if not add_end_point and hot_pixel_x == end_x:
                continue
            op = bound.ring.node
            to_front = bound.side is EdgeSide.LEFT
            if to_front and hot_pixel == op:
                continue
            elif not to_front and hot_pixel == op.prev:
                continue
            new_node = self.create_point_node(bound.ring, hot_pixel, op)
            if to_front:
                bound.ring.node = new_node
        else:
            return hot_pixel_start - 1
        return hot_pixel_index

    def insert_horizontal_local_minima_into_abl(self,
                                                operation_kind: OperationKind,
                                                subject_fill: Fill,
                                                clip_fill: Fill,
                                                top_y: Coordinate,
                                                scanbeams: List[Coordinate],
                                                minimums: List[LocalMinimum],
                                                minimums_index: int,
                                                active_bounds: List[Bound]
                                                ) -> int:
        while (minimums_index < len(minimums)
               and minimums[minimums_index].y == top_y
               and minimums[minimums_index].minimum_has_horizontal):
            minimum = minimums[minimums_index]
            minimum.initialize()
            self.insert_lm_left_and_right_bound(
                    operation_kind, subject_fill, clip_fill, scanbeams,
                    minimum.left_bound, minimum.right_bound, active_bounds)
            minimums_index += 1
        return minimums_index

    def insert_hot_pixels_in_path(self,
                                  bound: Bound,
                                  end_point: Point,
                                  add_end_point: bool) -> None:
        if end_point == bound.last_point:
            return
        start_x, start_y = bound.last_point
        end_x, end_y = end_point
        for index in range(self.current_hot_pixel_index, 0, -1):
            _, hot_pixel_y = self.hot_pixels[index]
            if hot_pixel_y > start_y:
                break
        else:
            index = 0
        _, end_point_y = end_point
        if start_x > end_x:
            while index < len(self.hot_pixels):
                _, y = self.hot_pixels[index]
                if y > start_y:
                    index += 1
                    continue
                elif y < end_y:
                    break
                first_index = index
                for index in range(index, len(self.hot_pixels)):
                    _, hot_pixel_y = self.hot_pixels[index]
                    if hot_pixel_y != y:
                        break
                else:
                    index = len(self.hot_pixels)
                last_index = index
                self.hot_pixel_set_right_to_left(
                        y, start_x, end_x, bound, first_index, last_index,
                        y != end_point_y or add_end_point)
        else:
            while index < len(self.hot_pixels):
                _, y = self.hot_pixels[index]
                if y > start_y:
                    index += 1
                    continue
                elif y < end_y:
                    break
                first_index = index
                for index in range(index, len(self.hot_pixels)):
                    _, hot_pixel_y = self.hot_pixels[index]
                    if hot_pixel_y != y:
                        break
                else:
                    index = len(self.hot_pixels)
                last_index = index
                self.hot_pixel_set_left_to_right(
                        y, start_x, end_x, bound, first_index, last_index,
                        y != end_point_y or add_end_point)
        bound.last_point = end_point

    def insert_lm_left_and_right_bound(self,
                                       operation_kind: OperationKind,
                                       subject_fill: Fill,
                                       clip_fill: Fill,
                                       scanbeams: List[Coordinate],
                                       left_bound: Bound,
                                       right_bound: Bound,
                                       active_bounds: List[Bound]) -> None:
        bound_index = insert_bounds(active_bounds, left_bound, right_bound)
        set_winding_count(active_bounds, bound_index, subject_fill, clip_fill)
        bound = active_bounds[bound_index]
        next_bound = active_bounds[bound_index + 1]
        next_bound.winding_count = bound.winding_count
        next_bound.opposite_winding_count = bound.opposite_winding_count
        if left_bound.is_contributing(operation_kind, subject_fill, clip_fill):
            self.add_local_minimum_point(bound.current_edge.bottom, bound,
                                         next_bound, active_bounds)
        # add edges' top to scanbeams
        insort_unique(scanbeams, bound.current_edge.top_y)
        if not next_bound.current_edge.is_horizontal:
            insort_unique(scanbeams, next_bound.current_edge.top_y)

    def insert_local_minima_into_abl(self,
                                     operation_kind: OperationKind,
                                     subject_fill: Fill,
                                     clip_fill: Fill,
                                     bot_y: Coordinate,
                                     scanbeams: List[Coordinate],
                                     minimums: List[LocalMinimum],
                                     minimums_index: int,
                                     active_bounds: List[Bound]) -> int:
        while (minimums_index < len(minimums)
               and minimums[minimums_index].y == bot_y):
            minimum = minimums[minimums_index]
            minimum.initialize()
            self.insert_lm_left_and_right_bound(
                    operation_kind, subject_fill, clip_fill, scanbeams,
                    minimum.left_bound, minimum.right_bound, active_bounds)
            minimums_index += 1
        return minimums_index

    def intersect_bounds(self,
                         point: Point,
                         operation_kind: OperationKind,
                         subject_fill: Fill,
                         clip_fill: Fill,
                         first_bound: Bound,
                         second_bound: Bound,
                         active_bounds: List[Bound]) -> None:
        first_bound_contributing = first_bound.ring is not None
        second_bound_contributing = second_bound.ring is not None
        # update winding counts,
        # assumes that first bound will be to the right of second bound
        # above the intersection
        if first_bound.operand_kind is second_bound.operand_kind:
            if first_bound.is_even_odd_fill(subject_fill, clip_fill):
                first_bound.winding_count, second_bound.winding_count = (
                    second_bound.winding_count, first_bound.winding_count)
            else:
                if first_bound.winding_count + second_bound.winding_delta == 0:
                    first_bound.winding_count = -first_bound.winding_count
                else:
                    first_bound.winding_count += second_bound.winding_delta
                if second_bound.winding_count - first_bound.winding_delta == 0:
                    second_bound.winding_count = -second_bound.winding_count
                else:
                    second_bound.winding_count -= first_bound.winding_delta
        else:
            if not second_bound.is_even_odd_fill(subject_fill, clip_fill):
                first_bound.opposite_winding_count += (
                    second_bound.winding_delta)
            else:
                first_bound.opposite_winding_count = int(
                        first_bound.opposite_winding_count == 0)
            if not first_bound.is_even_odd_fill(subject_fill, clip_fill):
                second_bound.opposite_winding_count -= (
                    first_bound.winding_delta)
            else:
                second_bound.opposite_winding_count = int(
                        second_bound.opposite_winding_count == 0)
        if first_bound.operand_kind is OperandKind.SUBJECT:
            first_bound_fill, first_bound_other_fill = subject_fill, clip_fill
        else:
            first_bound_fill, first_bound_other_fill = clip_fill, subject_fill
        if second_bound.operand_kind is OperandKind.SUBJECT:
            second_bound_fill, second_bound_other_fill = (subject_fill,
                                                          clip_fill)
        else:
            second_bound_fill, second_bound_other_fill = (clip_fill,
                                                          subject_fill)
        if first_bound_fill is Fill.POSITIVE:
            first_bound_winding_count = first_bound.winding_count
        elif first_bound_fill is Fill.NEGATIVE:
            first_bound_winding_count = -first_bound.winding_count
        else:
            first_bound_winding_count = abs(first_bound.winding_count)
        if second_bound_fill is Fill.POSITIVE:
            second_bound_winding_count = second_bound.winding_count
        elif second_bound_fill is Fill.NEGATIVE:
            second_bound_winding_count = -second_bound.winding_count
        else:
            second_bound_winding_count = abs(second_bound.winding_count)
        if first_bound_contributing and second_bound_contributing:
            if (first_bound_winding_count != 0
                    and first_bound_winding_count != 1
                    or second_bound_winding_count != 0
                    and second_bound_winding_count != 1
                    or (first_bound.operand_kind
                        is not second_bound.operand_kind)
                    and operation_kind is not OperationKind.XOR):
                self.add_local_maximum_point(point, first_bound, second_bound,
                                             active_bounds)
            else:
                self.add_point(first_bound, active_bounds, point)
                self.add_point(second_bound, active_bounds, point)
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif first_bound_contributing:
            if (second_bound_winding_count == 0
                    or second_bound_winding_count == 1):
                self.add_point(first_bound, active_bounds, point)
                second_bound.last_point = point
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif second_bound_contributing:
            if (first_bound_winding_count == 0
                    or first_bound_winding_count == 1):
                first_bound.last_point = point
                self.add_point(second_bound, active_bounds, point)
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)
                first_bound.ring, second_bound.ring = (second_bound.ring,
                                                       first_bound.ring)
        elif ((first_bound_winding_count == 0
               or first_bound_winding_count == 1)
              and (second_bound_winding_count == 0
                   or second_bound_winding_count == 1)):
            # neither bound is currently contributing
            if first_bound_other_fill is Fill.POSITIVE:
                first_bound_opposite_winding_count = (
                    first_bound.opposite_winding_count)
            elif first_bound_other_fill is Fill.NEGATIVE:
                first_bound_opposite_winding_count = (
                    -first_bound.opposite_winding_count)
            else:
                first_bound_opposite_winding_count = abs(
                        first_bound.opposite_winding_count)
            if second_bound_other_fill is Fill.POSITIVE:
                second_bound_opposite_winding_count = (
                    second_bound.opposite_winding_count)
            elif second_bound_other_fill is Fill.NEGATIVE:
                second_bound_opposite_winding_count = (
                    -second_bound.opposite_winding_count)
            else:
                second_bound_opposite_winding_count = abs(
                        second_bound.opposite_winding_count)
            if first_bound.operand_kind is not second_bound.operand_kind:
                self.add_local_minimum_point(point, first_bound, second_bound,
                                             active_bounds)
            elif (first_bound_winding_count == 1
                  and second_bound_winding_count == 1):
                if operation_kind is OperationKind.INTERSECTION:
                    if (first_bound_opposite_winding_count > 0
                            and second_bound_opposite_winding_count > 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                elif operation_kind is OperationKind.UNION:
                    if (first_bound_opposite_winding_count <= 0
                            and second_bound_opposite_winding_count <= 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                elif operation_kind is OperationKind.DIFFERENCE:
                    if (first_bound.operand_kind is OperandKind.CLIP
                            and first_bound_opposite_winding_count > 0
                            and second_bound_opposite_winding_count > 0
                            or first_bound.operand_kind is OperandKind.SUBJECT
                            and first_bound_opposite_winding_count <= 0
                            and second_bound_opposite_winding_count <= 0):
                        self.add_local_minimum_point(point, first_bound,
                                                     second_bound,
                                                     active_bounds)
                else:
                    self.add_local_minimum_point(point, first_bound,
                                                 second_bound,
                                                 active_bounds)
            else:
                first_bound.side, second_bound.side = (second_bound.side,
                                                       first_bound.side)

    def process_collinear_edges(self,
                                first_node: PointNode,
                                second_node: PointNode) -> bool:
        # neither point assigned to a ring (deleted points)
        if first_node.ring is None or second_node.ring is None:
            return False
        if self.remove_duplicate_points(first_node, second_node):
            return True
        if not has_collinear_edge(first_node, second_node):
            if first_node.ring is second_node.ring:
                self.correct_self_intersection(first_node, second_node)
                return True
            return False
        if first_node.ring is second_node.ring:
            self.process_collinear_edges_same_ring(first_node, second_node)
        else:
            self.process_collinear_edges_different_rings(first_node,
                                                         second_node)
        return True

    def process_collinear_edges_different_rings(self,
                                                first_node: PointNode,
                                                second_node: PointNode
                                                ) -> None:
        first_ring = first_node.ring
        second_ring = second_node.ring
        first_ring_is_larger = abs(first_ring.area) > abs(second_ring.area)
        path = find_start_and_end_of_collinear_edges(first_node, second_node)
        # this should result in two rings becoming one
        pt1, _ = fix_collinear_path(path)
        if pt1 is None:
            self.remove_ring(first_ring, False)
            self.remove_ring(second_ring, False)
            return
        # rings should merge into a single ring of the same orientation,
        # therefore we we will need to replace one ring with the other
        union_ring = first_ring if first_ring_is_larger else second_ring
        outsider_ring = second_ring if first_ring_is_larger else first_ring
        union_ring.node = pt1
        union_ring.update_points()
        union_ring.recalculate_stats()
        if union_ring.size < 3:
            self.remove_ring_and_points(union_ring, False)
        self.remove_ring(outsider_ring, False)

    def process_collinear_edges_same_ring(self,
                                          first_node: PointNode,
                                          second_node: PointNode) -> None:
        original_ring = first_node.ring
        # as they are the same ring that are forming a collinear edge
        # we should expect the creation of two different rings
        path = find_start_and_end_of_collinear_edges(first_node, second_node)
        pt1, pt2 = fix_collinear_path(path)
        if pt1 is None:
            # if pt1 is none, both values are nones,
            # this mean the ring was removed during this processing
            self.remove_ring(original_ring, False)
        elif pt2 is None:
            # if a single point is only returned, we simply removed a spike,
            # in this case we don't need to worry about parent or children
            # and we simply need to set the points and clear the area
            original_ring.node = pt1
            original_ring.recalculate_stats()
        else:
            # if we have two separate points,
            # the ring has split into two different rings
            ring_new = self.create_ring()
            ring_new.node = pt2
            ring_new.recalculate_stats()
            ring_new.update_points()
            original_ring.node = pt1
            original_ring.recalculate_stats()

    def process_edges_at_top_of_scanbeam(self,
                                         operation_kind: OperationKind,
                                         subject_fill: Fill,
                                         clip_fill: Fill,
                                         top_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         active_bounds: List[Bound],
                                         minimums_index: int,
                                         minimums: List[LocalMinimum]
                                         ) -> Tuple[List[Bound], int]:
        bound_index = 0
        while bound_index < len(active_bounds):
            bound = active_bounds[bound_index]
            if bound is None:
                bound_index += 1
                continue
            # 1) process maxima,
            # treating them as if they are "bent" horizontal edges,
            # but exclude maxima with horizontal edges
            is_maxima_edge = bound.is_maxima(top_y)
            if is_maxima_edge:
                maximum_bound_index = find(bound.maximum_bound, active_bounds)
                is_maxima_edge = (maximum_bound_index == len(active_bounds)
                                  or not (active_bounds[maximum_bound_index]
                                          .current_edge.is_horizontal)
                                  and (active_bounds[maximum_bound_index]
                                       .is_maxima(top_y)))
                if is_maxima_edge:
                    bound_index = self.do_maxima(
                            operation_kind, subject_fill, clip_fill,
                            bound_index, maximum_bound_index, active_bounds)
                    continue
            # 2) promote horizontal edges
            bound = active_bounds[bound_index]
            if bound.is_intermediate(top_y) and bound.next_edge.is_horizontal:
                if bound.ring is not None:
                    self.insert_hot_pixels_in_path(
                            bound, bound.current_edge.top, False)
                bound.to_next_edge(scanbeams)
                if bound.ring is not None:
                    self.add_point_to_ring(bound, bound.current_edge.bottom)
            else:
                bound.current_x = bound.current_edge.get_current_x(top_y)
            bound_index += 1
        active_bounds = list(filter(partial(is_not, None), active_bounds))
        minimums_index = self.insert_horizontal_local_minima_into_abl(
                operation_kind, subject_fill, clip_fill, top_y, scanbeams,
                minimums, minimums_index, active_bounds)
        active_bounds = self.process_horizontals(
                operation_kind, subject_fill, clip_fill, top_y, scanbeams,
                active_bounds)
        # 4) promote intermediate vertices
        for bound in active_bounds:
            if bound.is_intermediate(top_y):
                if bound.ring is not None:
                    self.add_point_to_ring(bound, bound.current_edge.top)
                bound.to_next_edge(scanbeams)
        return active_bounds, minimums_index

    def process_horizontal(self,
                           operation_kind: OperationKind,
                           subject_fill: Fill,
                           clip_fill: Fill,
                           scanline_y: Coordinate,
                           scanbeams: List[Coordinate],
                           bound_index: int,
                           active_bounds: List[Optional[Bound]]) -> int:
        bound = active_bounds[bound_index]
        return (self.process_horizontal_left_to_right
                if bound.current_edge.bottom_x < bound.current_edge.top_x
                else self.process_horizontal_right_to_left)(
                operation_kind, subject_fill, clip_fill, scanline_y, scanbeams,
                bound_index, active_bounds)

    def process_horizontals(self,
                            operation_kind: OperationKind,
                            subject_fill: Fill,
                            clip_fill: Fill,
                            scanline_y: Coordinate,
                            scanbeams: List[Coordinate],
                            active_bounds: List[Bound]) -> List[Bound]:
        active_bounds = list(active_bounds)
        index = 0
        while index < len(active_bounds):
            bound = active_bounds[index]
            if bound is not None and bound.current_edge.is_horizontal:
                index = self.process_horizontal(
                        operation_kind, subject_fill, clip_fill, scanline_y,
                        scanbeams, index, active_bounds)
            else:
                index += 1
        return list(filter(partial(is_not, None), active_bounds))

    def process_horizontal_left_to_right(self,
                                         operation_kind: OperationKind,
                                         subject_fill: Fill,
                                         clip_fill: Fill,
                                         scanline_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         bound_index: int,
                                         active_bounds: List[Optional[Bound]]
                                         ) -> int:
        shifted = False
        result = bound_index
        bound = active_bounds[bound_index]
        is_maxima_edge = bound.is_maxima(scanline_y)
        maximum_bound_index = len(active_bounds)
        if is_maxima_edge:
            maximum_bound_index = find(bound.maximum_bound, active_bounds)
        hot_pixel_index = self.current_hot_pixel_index
        for hot_pixel_index in range(hot_pixel_index, len(self.hot_pixels)):
            hot_pixel_x, hot_pixel_y = self.hot_pixels[hot_pixel_index]
            if ((hot_pixel_y, bound.current_edge.bottom_x)
                    <= (scanline_y, hot_pixel_x)):
                break
        else:
            hot_pixel_index = len(self.hot_pixels)
        for next_bound_index in range(bound_index + 1, len(active_bounds)):
            next_bound = active_bounds[next_bound_index]
            if next_bound is None:
                continue
            # insert extra coordinates into horizontal edges
            # (in output polygons)
            # wherever hot pixels touch these horizontal edges,
            # this helps 'simplifying' polygons
            # (i.e. if the simplify property is set)
            for hot_pixel_index in range(hot_pixel_index,
                                         len(self.hot_pixels)):
                hot_pixel = hot_pixel_x, hot_pixel_y = (
                    self.hot_pixels[hot_pixel_index])
                if (hot_pixel_y != scanline_y
                        or hot_pixel_x >= round_half_up(next_bound.current_x)
                        or hot_pixel_x >= bound.current_edge.top_x):
                    break
                if bound.ring is not None:
                    self.add_point_to_ring(bound, hot_pixel)
            else:
                hot_pixel_index = len(self.hot_pixels)
            if are_floats_greater_than(next_bound.current_x,
                                       float(bound.current_edge.top_x)):
                break
            # break if we've got to the end of an intermediate horizontal edge,
            # smaller dx's are to the right of larger dx's above the horizontal
            if (round_half_up(next_bound.current_x) == bound.current_edge.top_x
                    and bound.next_edge_index < len(bound.edges)
                    and bound.current_edge.slope < bound.next_edge.slope):
                break
            # may be done multiple times
            if bound.ring is not None:
                self.add_point_to_ring(
                        bound,
                        (round_half_up(next_bound.current_x), scanline_y))
            # so far we're still in range of the horizontal edge
            # but make sure we're at the last of consecutive horizontals
            # when matching with maximum bound
            if is_maxima_edge and next_bound_index == maximum_bound_index:
                if bound.ring is not None and next_bound.ring is not None:
                    self.add_local_maximum_point(bound.current_edge.top, bound,
                                                 next_bound, active_bounds)
                active_bounds[maximum_bound_index] = None
                active_bounds[bound_index] = None
                return result + (not shifted)
            self.intersect_bounds((round_half_up(next_bound.current_x),
                                   scanline_y), operation_kind,
                                  subject_fill, clip_fill, bound,
                                  next_bound, active_bounds)
            active_bounds[bound_index], active_bounds[next_bound_index] = (
                active_bounds[next_bound_index], active_bounds[bound_index])
            bound_index = next_bound_index
            bound = active_bounds[bound_index]
            shifted = True
        if bound.ring is not None:
            for hot_pixel_index in range(hot_pixel_index,
                                         len(self.hot_pixels)):
                hot_pixel = hot_pixel_x, hot_pixel_y = (
                    self.hot_pixels[hot_pixel_index])
                if (hot_pixel_y != scanline_y
                        or hot_pixel_x >= bound.current_edge.top_x):
                    break
                self.add_point_to_ring(bound, hot_pixel)
        if bound.ring is not None:
            self.add_point_to_ring(bound, bound.current_edge.top)
        if bound.next_edge_index < len(bound.edges):
            bound.to_next_edge(scanbeams)
        else:
            active_bounds[bound_index] = None
        return result + (not shifted)

    def process_horizontal_right_to_left(self,
                                         operation_kind: OperationKind,
                                         subject_fill: Fill,
                                         clip_fill: Fill,
                                         scanline_y: Coordinate,
                                         scanbeams: List[Coordinate],
                                         bound_index: int,
                                         active_bounds: List[Optional[Bound]]
                                         ) -> int:
        bound = active_bounds[bound_index]
        result = bound_index + 1
        is_maxima_edge = bound.is_maxima(scanline_y)
        maximum_bound_index = len(active_bounds)
        if is_maxima_edge:
            maximum_bound_index = find(bound.maximum_bound, active_bounds)
        hot_pixel_index = self.current_hot_pixel_index
        for hot_pixel_index in range(hot_pixel_index, len(self.hot_pixels)):
            hot_pixel_x, hot_pixel_y = self.hot_pixels[hot_pixel_index]
            if ((hot_pixel_y, hot_pixel_x)
                    >= (scanline_y, bound.current_edge.top_x)):
                break
        else:
            hot_pixel_index = len(self.hot_pixels)
        hot_pixel_index -= 1
        bound = active_bounds[bound_index]
        for prev_bound_index in range(bound_index - 1, -1, -1):
            prev_bound = active_bounds[prev_bound_index]
            if prev_bound is None:
                continue
            for hot_pixel_index in range(hot_pixel_index, -1, -1):
                hot_pixel = hot_pixel_x, hot_pixel_y = (
                    self.hot_pixels[hot_pixel_index])
                if (hot_pixel_y != scanline_y
                        or hot_pixel_x <= round_half_up(prev_bound.current_x)
                        or hot_pixel_x <= bound.current_edge.top_x):
                    break
                if bound.ring is not None:
                    self.add_point_to_ring(bound, hot_pixel)
            else:
                hot_pixel_index = -1
            if are_floats_less_than(prev_bound.current_x,
                                    float(bound.current_edge.top_x)):
                break
            # break if we've got to the end of an intermediate horizontal edge,
            # smaller dx's are to the right of larger dx's above the horizontal
            if (round_half_up(prev_bound.current_x) == bound.current_edge.top_x
                    and bound.next_edge_index < len(bound.edges)
                    and bound.current_edge.slope < bound.next_edge.slope):
                break
            # may be done multiple times
            if bound.ring is not None:
                self.add_point_to_ring(
                        bound,
                        (round_half_up(prev_bound.current_x), scanline_y))
            # so far we're still in range of the horizontal edge
            # but make sure we're at the last of consecutive horizontals
            # when matching with maximum bound
            if is_maxima_edge and prev_bound_index == maximum_bound_index:
                if bound.ring is not None and prev_bound.ring is not None:
                    self.add_local_maximum_point(bound.current_edge.top, bound,
                                                 prev_bound, active_bounds)
                active_bounds[prev_bound_index] = None
                active_bounds[bound_index] = None
                return result
            self.intersect_bounds((round_half_up(prev_bound.current_x),
                                   scanline_y), operation_kind, subject_fill,
                                  clip_fill, prev_bound, bound, active_bounds)
            active_bounds[prev_bound_index], active_bounds[bound_index] = (
                active_bounds[bound_index], active_bounds[prev_bound_index])
            bound_index = prev_bound_index
            bound = active_bounds[bound_index]
        if bound.ring is not None:
            for hot_pixel_index in range(hot_pixel_index, -1, -1):
                hot_pixel = hot_pixel_x, hot_pixel_y = (
                    self.hot_pixels[hot_pixel_index])
                if (hot_pixel_y != scanline_y
                        or hot_pixel_x <= bound.current_edge.top_x):
                    break
                self.add_point_to_ring(bound, hot_pixel)
        if bound.ring is not None:
            self.add_point_to_ring(bound, bound.current_edge.top)
        if bound.next_edge_index < len(bound.edges):
            bound.to_next_edge(scanbeams)
        else:
            active_bounds[bound_index] = None
        return result

    def process_intersections(self,
                              top_y: Coordinate,
                              operation_kind: OperationKind,
                              subject_fill: Fill,
                              clip_fill: Fill,
                              active_bounds: List[Bound]) -> None:
        if not active_bounds:
            return
        update_current_x(active_bounds, top_y)
        _, intersections = build_intersect_list(active_bounds)
        if not intersections:
            return
        self.process_intersect_list(sorted(intersections), operation_kind,
                                    subject_fill, clip_fill, active_bounds)

    def process_intersect_list(self, intersections: List[IntersectNode],
                               operation_kind: OperationKind,
                               subject_fill: Fill,
                               clip_fill: Fill,
                               active_bounds: List[Bound]) -> None:
        for index in range(len(intersections)):
            first_index = find_if(intersections[index].has_bound,
                                  active_bounds)
            second_index = first_index + 1
            if not intersections[index].has_bound(active_bounds[second_index]):
                for next_index in range(index + 1, len(intersections)):
                    next_node = intersections[next_index]
                    candidate_first_index = find_if(next_node.has_bound,
                                                    active_bounds)
                    candidate_second_index = candidate_first_index + 1
                    if next_node.has_bound(
                            active_bounds[candidate_second_index]):
                        first_index = candidate_first_index
                        second_index = candidate_second_index
                        break
                else:
                    raise RuntimeError('Could not properly correct '
                                       'intersection order.')
                intersections[index], intersections[next_index] = (
                    intersections[next_index], intersections[index])
            self.intersect_bounds(round_point(intersections[index].point),
                                  operation_kind, subject_fill, clip_fill,
                                  intersections[index].first_bound,
                                  intersections[index].second_bound,
                                  active_bounds)
            active_bounds[first_index], active_bounds[second_index] = (
                active_bounds[second_index], active_bounds[first_index])

    def process_single_intersection(self,
                                    op_j: PointNode,
                                    op_k: PointNode,
                                    connection_map: ConnectionMap) -> None:
        ring_j = op_j.ring
        ring_k = op_k.ring
        if ring_j is ring_k:
            return
        if not ring_j.is_hole and not ring_k.is_hole:
            # both are not holes, nothing to do
            return
        if not ring_j.is_hole:
            ring_origin = ring_j
            ring_parent = ring_origin
            ring_search = ring_k
            op_origin_1 = op_j
            op_origin_2 = op_k
        elif not ring_k.is_hole:
            ring_origin = ring_k
            ring_parent = ring_origin
            ring_search = ring_j
            op_origin_1 = op_k
            op_origin_2 = op_j
        else:
            # both are holes,
            # order doesn't matter
            ring_origin = ring_j
            ring_parent = ring_origin.parent
            ring_search = ring_k
            op_origin_1 = op_j
            op_origin_2 = op_k
        if ring_parent is not ring_search.parent:
            # the two holes do not have the same parent,
            # do not add them, simply return
            return
        found = False
        iList = deque()
        nodes_pairs_indices_to_remove = set()
        nodes_pairs = connection_map[id(ring_search)]
        for index, (op1, op2) in enumerate(nodes_pairs):
            if op1.ring is None or op2.ring is None:
                nodes_pairs_indices_to_remove.add(index)
                continue
            it_ring2 = op2.ring
            if it_ring2 is ring_origin:
                found = True
                if op_origin_1 != op2:
                    iList.append((ring_search, (op1, op2)))
                    break
        if nodes_pairs_indices_to_remove:
            nodes_pairs[:] = [nodes_pair
                              for index, nodes_pair in enumerate(nodes_pairs)
                              if index not in nodes_pairs_indices_to_remove]
        if not iList:
            visited = {id(ring_search)}
            for op1, op2 in nodes_pairs:
                it_ring = op2.ring
                if (it_ring is not ring_search and op_origin_2 != op2
                        and it_ring is not None
                        and (ring_parent is it_ring
                             or ring_parent is it_ring.parent)
                        and not is_float_almost_zero(it_ring.area)
                        and self.find_intersect_loop(
                                connection_map, iList, ring_parent,
                                ring_origin, it_ring, visited, op_origin_2,
                                op2)):
                    found = True
                    iList.appendleft((ring_search, (op1, op2)))
                    break
        if not found:
            connection_map[id(ring_origin)].append((op_origin_1, op_origin_2))
            connection_map[id(ring_search)].append((op_origin_2, op_origin_1))
            return
        if not iList:
            # the situation where both origin and search are holes
            # might have a missing search condition,
            # we must check if a new pair must be added
            missing = True
            # check for direct connection
            for op1, op2 in connection_map[id(ring_origin)]:
                it_ring2 = op2.ring
                if it_ring2 is ring_search:
                    missing = False
            if missing:
                connection_map[id(ring_origin)].append((op_origin_1,
                                                        op_origin_2))
            return
        if ring_origin.is_hole:
            for index, (ring_itr, (op1, op2)) in enumerate(iList):
                if not ring_itr.is_hole:
                    op1, op_origin_1 = op_origin_1, op1
                    op2, op_origin_2 = op_origin_2, op2
                    iList[index] = (ring_origin, (op1, op2))
                    ring_origin = ring_itr
                    ring_parent = ring_origin
                    break
        origin_is_hole = ring_origin.is_hole
        # switch
        op_origin_1_next = op_origin_1.next
        op_origin_2_next = op_origin_2.next
        op_origin_1.next = op_origin_2_next
        op_origin_2.next = op_origin_1_next
        op_origin_1_next.prev = op_origin_2
        op_origin_2_next.prev = op_origin_1
        for _, (op1, op2) in iList:
            op_search_1 = op1
            op_search_2 = op2
            op_search_1_next = op_search_1.next
            op_search_2_next = op_search_2.next
            op_search_1.next = op_search_2_next
            op_search_2.next = op_search_1_next
            op_search_1_next.prev = op_search_2
            op_search_2_next.prev = op_search_1
        ring_new = self.create_ring()
        ring_origin.corrected = False
        area_1, size_1, box1 = op_origin_1.stats
        area_2, size_2, box2 = op_origin_2.stats
        if origin_is_hole and area_1 < 0.:
            ring_origin.node = op_origin_1
            ring_origin.set_stats(area_1, size_1, box1)
            ring_new.node = op_origin_2
            ring_new.set_stats(area_2, size_2, box2)
        else:
            ring_origin.node = op_origin_2
            ring_origin.set_stats(area_2, size_2, box2)
            ring_new.node = op_origin_1
            ring_new.set_stats(area_1, size_1, box1)
        ring_origin.update_points()
        ring_new.update_points()
        ring_origin.bottom_node = None
        for ring_itr, _ in iList:
            ring_itr.bottom_node = None
            if origin_is_hole:
                self.replace_ring(ring_itr, ring_origin)
            else:
                self.replace_ring(ring_itr, ring_origin.parent)
        if origin_is_hole:
            self.assign_as_child(ring_new, ring_origin)
            # the parent ring in this situation might need to give up children
            # to the new ring
            for c in ring_parent.children:
                if c is None:
                    continue
                if c.is_subset_of(ring_new):
                    self.reassign_as_child(c, ring_new)
        else:
            # the new ring and the origin ring need to be siblings
            # however some children ring from the ring origin might
            # need to be re-assigned to the new ring
            self.assign_as_sibling(ring_new, ring_origin)
            for c in ring_origin.children:
                if c is None:
                    continue
                if c.is_subset_of(ring_new):
                    self.reassign_as_child(c, ring_new)
        move_list = []
        for ring, _ in iList:
            nodes_pairs = connection_map[id(ring)]
            for op1, op2 in nodes_pairs:
                it_ring = op1.ring
                it_ring2 = op2.ring
                if it_ring is None or it_ring2 is None or it_ring is it_ring2:
                    continue
                if it_ring.is_hole or it_ring2.is_hole:
                    move_list.append((it_ring, (op1, op2)))
            nodes_pairs.clear()
        nodes_pairs = connection_map[id(ring_origin)]
        nodes_pairs_indices_to_remove = set()
        for index, (op1, op2) in enumerate(nodes_pairs):
            it_ring = op1.ring
            it_ring2 = op2.ring
            if it_ring is None or it_ring2 is None or it_ring is it_ring2:
                nodes_pairs_indices_to_remove.add(index)
                continue
            if it_ring is not ring_origin:
                if it_ring.is_hole or it_ring2.is_hole:
                    move_list.append((it_ring, (op1, op2)))
                nodes_pairs_indices_to_remove.add(index)
            else:
                if not (it_ring.is_hole or it_ring2.is_hole):
                    nodes_pairs_indices_to_remove.add(index)
        if nodes_pairs_indices_to_remove:
            nodes_pairs[:] = [nodes_pair
                              for index, nodes_pair in enumerate(nodes_pairs)
                              if index not in nodes_pairs_indices_to_remove]
        if move_list:
            for ring, nodes_pair in move_list:
                connection_map[id(ring)].append(nodes_pair)

    def reassign_as_child(self, ring: Ring, parent: Optional[Ring]) -> None:
        # reassigning a ring assumes it already has an existing parent
        if ((parent is None and ring.is_hole)
                or (parent is not None and ring.is_hole is parent.is_hole)):
            raise RuntimeError('Trying to re-assign a child '
                               'that is the same orientation as the parent')
        # remove the old child relationship
        old_children = (self.children
                        if ring.parent is None
                        else ring.parent.children)
        remove_from_children(ring, old_children)
        # add new child relationship
        children = self.children if parent is None else parent.children
        set_to_children(ring, children)
        ring.parent = parent

    def reassign_children_if_necessary(self,
                                       new_ring: Ring,
                                       sibling_ring: Ring,
                                       new_rings: List[Ring]) -> None:
        children = (self.children
                    if sibling_ring is None
                    else sibling_ring.children)
        for child in children:
            if child is None:
                continue
            if find(child, new_rings) < len(new_rings):
                continue
            if child.is_subset_of(new_ring):
                self.reassign_as_child(child, new_ring)

    def remove_duplicate_points(self,
                                first_node: PointNode,
                                second_node: PointNode) -> bool:
        if first_node.ring is second_node.ring:
            if first_node.next is second_node:
                first_node.next = second_node.next
                first_node.next.prev = first_node
                second_node.prev = second_node.next = second_node.ring = None
                if first_node.ring.node is second_node:
                    first_node.ring.node = first_node
                return True
            elif second_node.next is first_node:
                first_node.prev = second_node.prev
                first_node.prev.next = first_node
                second_node.prev = second_node.next = second_node.ring = None
                if first_node.ring.node is second_node:
                    first_node.ring.node = first_node
                return True
        while (first_node.next == first_node
               and first_node.next is not first_node):
            outsider = first_node.next
            first_node.next = outsider.next
            first_node.next.prev = first_node
            outsider.prev = outsider.next = outsider.ring = None
            if first_node.ring.node is outsider:
                first_node.ring.node = first_node
        while (first_node.prev == first_node
               and first_node.prev is not first_node):
            outsider = first_node.prev
            first_node.prev = outsider.prev
            first_node.prev.next = first_node
            outsider.prev = outsider.next = outsider.ring = None
            if first_node.ring.node is outsider:
                first_node.ring.node = first_node
        if first_node.next is first_node:
            self.remove_ring_and_points(first_node.ring, False)
            return True
        if second_node.ring is None:
            return True
        while (second_node.next == second_node
               and second_node.next is not second_node):
            outsider = second_node.next
            second_node.next = outsider.next
            second_node.next.prev = second_node
            outsider.prev = outsider.next = outsider.ring = None
            if second_node.ring.node is outsider:
                second_node.ring.node = second_node
        while (second_node.prev == second_node
               and second_node.prev is not second_node):
            outsider = second_node.prev
            second_node.prev = outsider.prev
            second_node.prev.next = second_node
            outsider.prev = outsider.next = outsider.ring = None
            if second_node.ring.node is outsider:
                second_node.ring.node = second_node
        if second_node.next is second_node:
            self.remove_ring_and_points(second_node.ring, False)
            return True
        return first_node.ring is None

    def remove_ring(self, ring: Ring,
                    remove_children: bool = True,
                    remove_from_parent: bool = True) -> None:
        # removes a ring and any children that might be under that ring
        for index, child in enumerate(ring.children):
            if child is None:
                continue
            if remove_children:
                self.remove_ring(child, True, False)
            ring.children[index] = None
        if remove_from_parent:
            # Remove the old child relationship
            old_children = (self.children
                            if ring.parent is None
                            else ring.parent.children)
            remove_from_children(ring, old_children)
        ring.node = None
        ring.reset_stats()

    def remove_ring_and_points(self,
                               ring: Ring,
                               remove_children: bool = True,
                               remove_from_parent: bool = True) -> None:
        for index, child in enumerate(ring.children):
            if child is None:
                continue
            if remove_children:
                self.remove_ring_and_points(child, True, False)
            ring.children[index] = None
        if remove_from_parent:
            # remove the old child relationship
            remove_from_children(ring,
                                 self.children
                                 if ring.parent is None
                                 else ring.parent.children)
        node = ring.node
        if node is not None:
            node.prev.next = None
            while node is not None:
                node.prev, node.next, node.ring, node = (None, None, None,
                                                         node.next)
        ring.node = None
        ring.reset_stats()

    def replace_ring(self,
                     original: Optional[Ring],
                     replacement: Ring) -> None:
        assert original is not replacement
        replacement_children = (self.children
                                if replacement is None
                                else replacement.children)
        original_children = original.children
        for index, child in enumerate(original_children):
            if child is None:
                continue
            child.parent = replacement
            set_to_children(child, replacement_children)
            original_children[index] = None
        # remove the old child relationship
        remove_from_children(original,
                             self.children
                             if original.parent is None
                             else original.parent.children)
        original.node = None
        original.reset_stats()

    def set_hole_state(self, bound: Bound, active_bounds: List[Bound]) -> None:
        bound_index = next(index
                           for index in range(len(active_bounds) - 1, -1, -1)
                           if active_bounds[index] is bound)
        bound_index -= 1
        bound_temp = None
        while bound_index >= 0:
            current_bound = active_bounds[bound_index]
            if current_bound is not None and current_bound.ring is not None:
                if bound_temp is None:
                    bound_temp = current_bound
                elif bound_temp.ring is current_bound.ring:
                    bound_temp = None
            bound_index -= 1
        if bound_temp is None:
            bound.ring.parent = None
            self.children.append(bound.ring)
        else:
            bound.ring.parent = bound_temp.ring
            bound_temp.ring.children.append(bound.ring)

    def update_current_hot_pixel_index(self, scanline_y: Coordinate) -> None:
        _, hot_pixel_y = self.hot_pixels[self.current_hot_pixel_index]
        while hot_pixel_y > scanline_y:
            self.current_hot_pixel_index += 1
            _, hot_pixel_y = self.hot_pixels[self.current_hot_pixel_index]
