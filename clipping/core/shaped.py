from abc import (ABC,
                 abstractmethod)
from collections import defaultdict
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (DefaultDict,
                    List,
                    Optional,
                    Union as Union_)

from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)
from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from clipping.hints import (Contour,
                            Mix,
                            Multipoint,
                            Multipolygon,
                            Multisegment,
                            Point,
                            Segment)
from . import bounding_box
from .enums import EdgeType
from .event import ShapedEvent as Event
from .events_queue import (BinaryEventsQueue as EventsQueue,
                           BinaryEventsQueueKey as EventsQueueKey)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    contour_to_segments,
                    sort_pair,
                    to_first_boundary_vertex,
                    to_multipolygon_base,
                    to_multipolygon_contours,
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
        if below_event is None:
            event.in_out = False
            event.other_in_out = True
        else:
            if event.from_left is below_event.from_left:
                event.in_out = not below_event.in_out
                event.other_in_out = below_event.other_in_out
            else:
                event.in_out = not below_event.other_in_out
                event.other_in_out = (not below_event.in_out
                                      if below_event.is_vertical
                                      else below_event.in_out)
            event.below_in_result_event = (below_event.below_in_result_event
                                           if (not self.in_result(below_event)
                                               or below_event.is_vertical)
                                           else below_event)
        event.in_result = self.in_result(event)

    def detect_intersection(self, below_event: Event, event: Event) -> bool:
        below_segment, segment = below_event.segment, event.segment
        relationship = segments_relationship(below_segment, segment)
        if relationship is SegmentsRelationship.OVERLAP:
            # segments overlap
            if below_event.from_left is event.from_left:
                raise ValueError('Edges of the same multipolygon '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            if starts_equal:
                start_min = start_max = None
            elif EventsQueueKey(event) < EventsQueueKey(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif (EventsQueueKey(event.complement)
                  < EventsQueueKey(below_event.complement)):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            if starts_equal:
                # both line segments are equal or share the left endpoint
                below_event.edge_type = EdgeType.NON_CONTRIBUTING
                event.edge_type = (EdgeType.SAME_TRANSITION
                                   if event.in_out is below_event.in_out
                                   else EdgeType.DIFFERENT_TRANSITION)
                if not ends_equal:
                    self.divide_segment(end_max.complement, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self.divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                self.divide_segment(start_min, end_min.start)
                self.divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self.divide_segment(start_max, end_min.start)
                self.divide_segment(start_min, start_max.start)
        elif (relationship is not SegmentsRelationship.NONE
              and event.start != below_event.start
              and event.end != below_event.end):
            # segments do not intersect_multipolygons at endpoints
            point = segments_intersection(below_segment, segment)
            if point != below_event.start and point != below_event.end:
                self.divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self.divide_segment(event, point)
        return False

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = Event(False, point, event.complement, event.from_left)
        right_event = Event(True, point, event, event.from_left)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)

    def fill_queue(self) -> None:
        for contour in to_multipolygon_contours(self.left):
            for segment in contour_to_segments(contour):
                self.register_segment(segment, True)
        for contour in to_multipolygon_contours(self.right):
            for segment in contour_to_segments(contour):
                self.register_segment(segment, False)

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
                    self.detect_intersection(below_event, above_event)
        elif event not in sweep_line:
            processed_events.append(event)
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            self.compute_fields(event, below_event)
            if (above_event is not None
                    and self.detect_intersection(event, above_event)):
                self.compute_fields(event, below_event)
                self.compute_fields(above_event, event)
            if (below_event is not None
                    and self.detect_intersection(below_event, event)):
                below_below_event = sweep_line.below(below_event)
                self.compute_fields(below_event, below_below_event)
                self.compute_fields(event, below_event)

    def register_segment(self, segment: Segment, from_left: bool) -> None:
        start, end = sort_pair(segment)
        start_event = Event(False, start, None, from_left)
        end_event = Event(True, end, start_event, from_left)
        start_event.complement = end_event
        self._events_queue.push(start_event)
        self._events_queue.push(end_event)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        while self._events_queue:
            self.process_event(self._events_queue.pop(), result, sweep_line)
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
        edge_type = event.edge_type
        return (edge_type is EdgeType.NORMAL
                and event.from_left is event.other_in_out
                or edge_type is EdgeType.DIFFERENT_TRANSITION)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        left_x_max = to_multipolygon_x_max(self.left)
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > left_x_max:
                break
            self.process_event(event, result, sweep_line)
        return result


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
        sweep_line = SweepLine()
        min_max_x = min(to_multipolygon_x_max(self.left),
                        to_multipolygon_x_max(self.right))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: Event) -> bool:
        edge_type = event.edge_type
        return (edge_type is EdgeType.NORMAL and not event.other_in_out
                or edge_type is EdgeType.SAME_TRANSITION)


class CompleteIntersection(Intersection):
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
                for event, next_event in zip(same_start_events,
                                             same_start_events[1:]):
                    if (event.from_left is not next_event.from_left
                            and event.segment == next_event.segment):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            multisegment.append(next_event.segment)
                if no_segment_found and all(not event.complement.in_result
                                            if event.is_right_endpoint
                                            else not event.in_result
                                            for event in same_start_events):
                    multipoint.append(start)
        multipolygon = events_to_multipolygon(events)
        return multipoint, multisegment, multipolygon


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
        return event.edge_type is EdgeType.NORMAL


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
        edge_type = event.edge_type
        return (edge_type is EdgeType.NORMAL and event.other_in_out
                or edge_type is EdgeType.SAME_TRANSITION)


def events_to_multipolygon(events: List[Event]) -> Multipolygon:
    are_internal = defaultdict(bool)
    holes = defaultdict(list)
    return _contours_to_multipolygon(
            _events_to_contours(_collect_events(events), are_internal, holes),
            are_internal, holes)


def _collect_events(events: List[Event]) -> List[Event]:
    result = sorted(
            [event
             for event in events
             if not event.is_right_endpoint and event.in_result
             or event.is_right_endpoint and event.complement.in_result],
            key=EventsQueueKey)
    for index, event in enumerate(result):
        event.position = index
        if event.is_right_endpoint:
            event.position, event.complement.position = (
                event.complement.position, event.position)
    return result


def _contours_to_multipolygon(contours: List[Contour],
                              are_internal: DefaultDict[int, bool],
                              holes: DefaultDict[int, List[int]]
                              ) -> Multipolygon:
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


def _events_to_contours(events: List[Event],
                        are_internal: DefaultDict[int, bool],
                        holes: DefaultDict[int, List[int]]) -> List[Contour]:
    depths, parents = defaultdict(int), {}
    processed = [False] * len(events)
    contours = []
    for index, event in enumerate(events):
        if processed[index]:
            continue

        position = index
        initial = event.start
        contour = [initial]
        steps = [event]
        while position >= index:
            step = events[position]
            if step.end == initial:
                break
            processed[position] = True
            steps.append(step)
            position = step.position
            processed[position] = True
            contour.append(events[position].start)
            position = _to_next_position(position, events, processed, index)
        position = index if position == -1 else position
        last_event = events[position]
        processed[position] = processed[last_event.position] = True

        _shrink_collinear_vertices(contour)
        if len(contour) < 3:
            continue

        contour_id = len(contours)

        is_internal = False
        if event.below_in_result_event is not None:
            below_in_result_contour_id = event.below_in_result_event.contour_id
            if not event.below_in_result_event.result_in_out:
                holes[below_in_result_contour_id].append(contour_id)
                parents[contour_id] = below_in_result_contour_id
                depths[contour_id] = depths[below_in_result_contour_id] + 1
                is_internal = True
            elif are_internal[below_in_result_contour_id]:
                below_in_result_parent_id = parents[below_in_result_contour_id]
                holes[below_in_result_parent_id].append(contour_id)
                parents[contour_id] = below_in_result_parent_id
                depths[contour_id] = depths[below_in_result_contour_id]
                is_internal = True
        are_internal[contour_id] = is_internal

        for step in steps:
            if step.is_right_endpoint:
                step.complement.result_in_out = True
                step.complement.contour_id = contour_id
            else:
                step.result_in_out = False
                step.contour_id = contour_id
        last_event.complement.result_in_out = True
        last_event.complement.contour_id = contour_id

        if depths[contour_id] & 1:
            # holes will be in clockwise order
            contour.reverse()

        contours.append(contour)
    return contours


def _shrink_collinear_vertices(contour: Contour) -> None:
    self_intersections, visited = set(), set()
    visit = visited.add
    for vertex in contour:
        if vertex in visited:
            self_intersections.add(vertex)
        else:
            visit(vertex)
    index = -len(contour) + 1
    while index < 0:
        while (max(2, -index) < len(contour)
               and contour[index + 1] not in self_intersections
               and (orientation(contour[index + 2], contour[index + 1],
                                contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index + 1]
        index += 1
    while index < len(contour):
        while (max(2, index) < len(contour)
               and contour[index - 1] not in self_intersections
               and (orientation(contour[index - 2], contour[index - 1],
                                contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index - 1]
        index += 1


def _to_next_position(position: int,
                      events: List[Event],
                      processed: List[bool],
                      original_index: int) -> int:
    result = position + 1
    point = events[position].start
    while result < len(events) and events[result].start == point:
        if not processed[result]:
            return result
        else:
            result += 1
    result = position - 1
    while result >= original_index and processed[result]:
        result -= 1
    return result
