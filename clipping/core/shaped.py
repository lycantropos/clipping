from abc import (ABC,
                 abstractmethod)
from collections import defaultdict
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (DefaultDict,
                    Iterable,
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
from .enums import OverlapKind
from .event import ShapedEvent as Event
from .events_queue import (BinaryEventsQueue as EventsQueue,
                           BinaryEventsQueueKey as EventsQueueKey)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    polygon_to_oriented_segments,
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
                below_event.overlap_kind = event.overlap_kind = (
                    OverlapKind.SAME_ORIENTATION
                    if event.interior_to_left is below_event.interior_to_left
                    else OverlapKind.DIFFERENT_ORIENTATION)
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
        left_event = Event(False, point, event.complement, event.from_left,
                           event.interior_to_left)
        right_event = Event(True, point, event, event.from_left,
                            event.interior_to_left)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)

    def fill_queue(self) -> None:
        for polygon in self.left:
            self.register_segments(polygon_to_oriented_segments(polygon), True)
        for polygon in self.right:
            self.register_segments(polygon_to_oriented_segments(polygon),
                                   False)

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

    def register_segments(self,
                          segments: Iterable[Segment],
                          from_left: bool) -> None:
        events_queue = self._events_queue
        for start, end in segments:
            inside_on_left = True
            if start > end:
                start, end = end, start
                inside_on_left = False
            start_event = Event(False, start, None, from_left, inside_on_left)
            end_event = Event(True, end, start_event, from_left,
                              inside_on_left)
            start_event.complement = end_event
            events_queue.push(start_event)
            events_queue.push(end_event)

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
        return (event.outside
                if event.from_left
                else event.inside or event.is_common_polyline_component)

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
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)


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
    are_internal = defaultdict(bool)
    holes = defaultdict(list)
    return _contours_to_multipolygon(
            _events_to_contours(_collect_events(events), are_internal, holes),
            are_internal, holes)


def _collect_events(events: List[Event]) -> List[Event]:
    return sorted([event
                   for event in events
                   if not event.is_right_endpoint and event.in_result
                   or event.is_right_endpoint and event.complement.in_result],
                  key=EventsQueueKey)


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
    for index, event in enumerate(events):
        event.position = index
    depths, parents = defaultdict(int), {}
    processed = [False] * len(events)
    contours = []
    connectivity = _to_events_connectivity(events)
    for index, event in enumerate(events):
        if processed[index]:
            continue
        position = index
        initial = event.start
        contour = [initial]
        contour_events = []
        cursor = event
        while cursor.end != initial:
            processed[position] = True
            contour_events.append(cursor)
            position = cursor.complement.position
            processed[position] = True
            contour.append(cursor.end)
            position = _to_next_position(position, processed, connectivity)
            if position is None:
                position = index
                break
            cursor = events[position]
        last_event = events[position]
        processed[position] = processed[last_event.complement.position] = True
        _shrink_collinear_vertices(contour)
        if len(contour) < 3:
            continue
        contour_id = len(contours)
        is_internal = False
        below_in_result_event = event.below_in_result_event
        if below_in_result_event is not None:
            below_in_result_contour_id = below_in_result_event.contour_id
            if not below_in_result_event.result_in_out:
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
        _update_contour_events(contour_events, contour_id)
        last_event.complement.result_in_out = True
        last_event.complement.contour_id = contour_id
        if depths[contour_id] % 2:
            # holes will be in clockwise order
            contour.reverse()
        contours.append(contour)
    return contours


def _update_contour_events(events: Iterable[Event], contour_id: int) -> None:
    for event in events:
        if event.is_right_endpoint:
            event.complement.result_in_out = True
            event.complement.contour_id = contour_id
        else:
            event.result_in_out = False
            event.contour_id = contour_id


def _to_events_connectivity(events: List[Event]) -> List[int]:
    events_count = len(events)
    result = [0] * events_count
    index = 0
    while index < events_count:
        current_start = events[index].start
        right_start_index = index
        while (index < events_count
               and events[index].start == current_start
               and events[index].is_right_endpoint):
            index += 1
        right_stop_index = index - 1
        left_start_index = index
        while index < events_count and events[index].start == current_start:
            index += 1
        left_stop_index = index - 1
        has_right_events = right_stop_index >= right_start_index
        has_left_events = left_stop_index >= left_start_index
        if has_right_events:
            result[right_start_index:right_stop_index] = range(
                    right_start_index + 1, right_stop_index + 1)
            result[right_stop_index] = (left_stop_index
                                        if has_left_events
                                        else right_start_index)
        if has_left_events:
            result[left_start_index] = (right_start_index
                                        if has_right_events
                                        else left_stop_index)
            result[left_start_index + 1:left_stop_index + 1] = range(
                    left_start_index, left_stop_index)
    return result


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
                      processed: List[bool],
                      connectivity: List[int]) -> Optional[int]:
    candidate = position
    while True:
        candidate = connectivity[candidate]
        if not processed[candidate]:
            return candidate
        elif candidate == position:
            return None
