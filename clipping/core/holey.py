from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (List,
                    Optional,
                    Union as Union_)

from reprit.base import generate_repr

from clipping.hints import (Contour,
                            Mix,
                            Multipoint,
                            Multipolygon,
                            Multisegment)
from . import bounding_box
from .event import (HoleyEvent as Event,
                    events_to_connectivity)
from .events_queue import (BinaryEventsQueueKey as EventsQueueKey,
                           HoleyEventsQueue as EventsQueue)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    pairwise,
                    polygon_to_oriented_segments,
                    shrink_collinear_vertices,
                    to_first_boundary_vertex,
                    to_multipolygon_base,
                    to_multipolygon_x_max,
                    to_rational_multipolygon)


class Operation(ABC):
    __slots__ = 'left', 'right', 'accurate', '_events_queue'

    def __init__(self,
                 left: Multipolygon,
                 right: Multipolygon,
                 accurate: bool) -> None:
        """
        Initializes operation.

        :param left: left operand.
        :param right: right operand.
        :param accurate:
            flag that tells whether to use slow but more accurate arithmetic
            for floating point numbers.
        """
        self.left = left
        self.right = right
        self.accurate = accurate
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Multipolygon, Mix]:
        """
        Computes result of the operation.
        """

    def compute_fields(self, event: Event, below_event: Optional[Event]
                       ) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_left
                                                is below_event.from_left)
                                            else below_event.interior_to_left)
            event.below_in_result_event = (below_event.below_in_result_event
                                           if (not self.in_result(below_event)
                                               or below_event.is_vertical)
                                           else below_event)
        event.in_result = self.in_result(event)

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        for polygon in self.left:
            events_queue.register_segments(
                    polygon_to_oriented_segments(polygon), True)
        for polygon in self.right:
            events_queue.register_segments(
                    polygon_to_oriented_segments(polygon), False)

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def normalize_operands(self) -> None:
        left, right = self.left, self.right
        if (self.accurate
                and not issubclass(to_multipolygon_base(left + right),
                                   Rational)):
            self.left, self.right = (to_rational_multipolygon(left),
                                     to_rational_multipolygon(right))

    def process_event(self, event: Event, processed_events: List[Event],
                      sweep_line: SweepLine) -> None:
        if event.is_right_endpoint:
            processed_events.append(event)
            event = event.complement
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)
        elif event not in sweep_line:
            processed_events.append(event)
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            self.compute_fields(event, below_event)
            if (above_event is not None
                    and self._events_queue.detect_intersection(event,
                                                               above_event)):
                self.compute_fields(event, below_event)
                self.compute_fields(above_event, event)
            if (below_event is not None
                    and self._events_queue.detect_intersection(below_event,
                                                               event)):
                below_below_event = sweep_line.below(below_event)
                self.compute_fields(below_event, below_below_event)
                self.compute_fields(event, below_event)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        events_queue = self._events_queue
        while events_queue:
            self.process_event(events_queue.pop(), result, sweep_line)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        if not (self.left and self.right):
            return self.left
        left_bounding_box = bounding_box.from_multipolygon(self.left)
        if bounding_box.disjoint_with(
                left_bounding_box, bounding_box.from_multipolygon(self.right)):
            return self.left
        self.right = bounding_box.to_coupled_polygons(left_bounding_box,
                                                      self.right)
        if not self.right:
            return self.left
        self.normalize_operands()
        return events_to_multipolygon(self.sweep())

    def in_result(self, event: Event) -> bool:
        return (event.outside
                if event.from_left
                else event.inside or event.is_common_polyline_component)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine()
        left_x_max = to_multipolygon_x_max(self.left)
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > left_x_max:
                break
            self.process_event(event, result, sweep_line)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        if not (self.left and self.right):
            return [], [], []
        left_bounding_box = bounding_box.from_multipolygon(self.left)
        right_bounding_box = bounding_box.from_multipolygon(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return [], [], []
        self.left = bounding_box.to_intersecting_polygons(right_bounding_box,
                                                          self.left)
        self.right = bounding_box.to_intersecting_polygons(left_bounding_box,
                                                           self.right)
        if not (self.left and self.right):
            return [], [], []
        self.normalize_operands()
        events = sorted(self.sweep(),
                        key=EventsQueueKey)
        multipoint = []  # type: Multipoint
        multisegment = []  # type: Multisegment
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if (all(event.is_right_endpoint or not event.in_result
                    for event in same_start_events)
                    and not all_equal(event.from_left
                                      for event in same_start_events)):
                no_segment_found = True
                for event, next_event in pairwise(same_start_events):
                    if (event.from_left is not next_event.from_left
                            and event.segment == next_event.segment):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            multisegment.append(next_event.segment)
                if no_segment_found and all(not event.primary.in_result
                                            for event in same_start_events):
                    multipoint.append(start)
        return multipoint, multisegment, events_to_multipolygon(events)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine()
        min_max_x = min(to_multipolygon_x_max(self.left),
                        to_multipolygon_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        if not (self.left and self.right):
            return []
        left_bounding_box = bounding_box.from_multipolygon(self.left)
        right_bounding_box = bounding_box.from_multipolygon(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return []
        self.left = bounding_box.to_coupled_polygons(right_bounding_box,
                                                     self.left)
        self.right = bounding_box.to_coupled_polygons(left_bounding_box,
                                                      self.right)
        if not (self.left and self.right):
            return []
        self.normalize_operands()
        return events_to_multipolygon(self.sweep())

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine()
        min_max_x = min(to_multipolygon_x_max(self.left),
                        to_multipolygon_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding_box.disjoint_with(
                bounding_box.from_multipolygon(self.left),
                bounding_box.from_multipolygon(self.right)):
            result = self.left + self.right
            result.sort(key=to_first_boundary_vertex)
            return result
        self.normalize_operands()
        return events_to_multipolygon(self.sweep())

    def in_result(self, event: Event) -> bool:
        return not event.is_overlap


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding_box.disjoint_with(
                bounding_box.from_multipolygon(self.left),
                bounding_box.from_multipolygon(self.right)):
            result = self.left + self.right
            result.sort(key=to_first_boundary_vertex)
            return result
        self.normalize_operands()
        return events_to_multipolygon(self.sweep())

    def in_result(self, event: Event) -> bool:
        return (event.outside
                or not event.from_left and event.is_common_region_boundary)


def events_to_multipolygon(events: List[Event]) -> Multipolygon:
    events = sorted([event for event in events if event.primary.in_result],
                    key=EventsQueueKey)
    for index, event in enumerate(events):
        event.position = index
    are_internal, depths, holes, parents = [], [], [], []
    processed = [False] * len(events)
    contours = []
    connectivity = events_to_connectivity(events)
    for index, event in enumerate(events):
        if processed[index]:
            continue
        contour_id = len(contours)
        _compute_relations(event, contour_id, are_internal, depths, holes,
                           parents)
        contour = _events_to_contour(event, events, contour_id, connectivity,
                                     processed)
        shrink_collinear_vertices(contour)
        if depths[contour_id] % 2:
            # holes will be in clockwise order
            contour.reverse()
        contours.append(contour)
    result = []
    for index, contour in enumerate(contours):
        if are_internal[index]:
            # hole of a hole is an external polygon
            result.extend((contours[hole_index],
                           [contours[hole_hole_index]
                            for hole_hole_index in holes[hole_index]])
                          for hole_index in holes[index])
        else:
            result.append((contour, [contours[hole_index]
                                     for hole_index in holes[index]]))
    return result


def _compute_relations(event: Event,
                       contour_id: int,
                       are_internal: List[bool],
                       depths: List[int],
                       holes: List[List[int]],
                       parents: List[Optional[int]]) -> None:
    depth = 0
    parent = None
    is_internal = False
    below_in_result_event = event.below_in_result_event
    if below_in_result_event is not None:
        below_in_result_contour_id = below_in_result_event.contour_id
        if not below_in_result_event.result_in_out:
            holes[below_in_result_contour_id].append(contour_id)
            parent = below_in_result_contour_id
            depth = depths[below_in_result_contour_id] + 1
            is_internal = True
        elif are_internal[below_in_result_contour_id]:
            below_in_result_parent_id = parents[below_in_result_contour_id]
            holes[below_in_result_parent_id].append(contour_id)
            parent = below_in_result_parent_id
            depth = depths[below_in_result_contour_id]
            is_internal = True
    holes.append([])
    parents.append(parent)
    depths.append(depth)
    are_internal.append(is_internal)


def _events_to_contour(cursor: Event,
                       events: List[Event],
                       contour_id: int,
                       connectivity: List[int],
                       processed: List[bool]) -> Contour:
    contour_start = cursor.start
    contour = [contour_start]
    contour_events = [cursor]
    complement_position = cursor.complement.position
    vertices_positions = {contour_start: 0}
    while cursor.end != contour_start:
        vertex = cursor.end
        if vertex in vertices_positions:
            # vertices loop found, i.e. contour has self-intersection
            previous_vertex_position = vertices_positions[vertex]
            del contour[previous_vertex_position:]
            del contour_events[previous_vertex_position:]
        else:
            vertices_positions[vertex] = len(contour)
        contour.append(vertex)
        position = _to_next_position(complement_position, processed,
                                     connectivity)
        if position is None:
            break
        cursor = events[position]
        contour_events.append(cursor)
        complement_position = cursor.complement.position
    for event in contour_events:
        processed[event.position] = processed[event.complement.position] = True
        if event.is_right_endpoint:
            event.complement.result_in_out = True
            event.complement.contour_id = contour_id
        else:
            event.result_in_out = False
            event.contour_id = contour_id
    return contour


def _to_next_position(position: int,
                      processed: List[bool],
                      connectivity: List[int]) -> Optional[int]:
    candidate = position
    while True:
        candidate = connectivity[candidate]
        if not processed[candidate]:
            return candidate
        elif candidate == position:
            return None
