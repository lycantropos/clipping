from abc import (ABC,
                 abstractmethod)
from collections import defaultdict
from numbers import Rational
from typing import (DefaultDict,
                    List,
                    Optional,
                    Type)

from bentley_ottmann import linear
from bentley_ottmann.angular import (Orientation,
                                     to_orientation)
from reprit.base import generate_repr

from clipping.hints import (Contour,
                            Multipolygon,
                            Point,
                            Segment)
from .enums import EdgeType
from .event import Event
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine
from .utils import (to_bounding_box,
                    to_first_boundary_vertex,
                    to_multipolygon_base,
                    to_multipolygon_contours,
                    to_multipolygon_x_max,
                    to_rational_multipolygon,
                    to_segments)


class Operation(ABC):
    __slots__ = ('left', 'right', '_events_queue')

    def __init__(self,
                 left: Multipolygon,
                 right: Multipolygon) -> None:
        self.left = left
        self.right = right
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    def compute(self) -> Multipolygon:
        return events_to_multipolygon(self.sweep())

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        while self._events_queue:
            self.process_event(self._events_queue.pop(), result, sweep_line)
        return result

    def fill_queue(self) -> None:
        for contour in to_multipolygon_contours(self.left):
            for segment in to_segments(contour):
                self.register_segment(segment, True)
        for contour in to_multipolygon_contours(self.right):
            for segment in to_segments(contour):
                self.register_segment(segment, False)

    def register_segment(self, segment: Segment, from_left: bool) -> None:
        start, end = sorted(segment)
        start_event = Event(False, start, None, from_left, EdgeType.NORMAL)
        end_event = Event(True, end, start_event, from_left, EdgeType.NORMAL)
        start_event.complement = end_event
        self._events_queue.push(start_event)
        self._events_queue.push(end_event)

    def process_event(self, event: Event, processed_events: List[Event],
                      sweep_line: SweepLine) -> None:
        start_x, _ = event.start
        sweep_line.move_to(start_x)
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
            if above_event is not None:
                if self.detect_intersection(event, above_event) == 2:
                    self.compute_fields(event, below_event)
                    self.compute_fields(above_event, event)
            if below_event is not None:
                if self.detect_intersection(below_event, event) == 2:
                    below_below_event = sweep_line.below(below_event)
                    self.compute_fields(below_event, below_below_event)
                    self.compute_fields(event, below_event)

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

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def detect_intersection(self, event: Event, above_event: Event) -> int:
        intersections = linear.find_intersections(event.segment,
                                                  above_event.segment)
        if not intersections:
            # no intersection
            return 0
        elif len(intersections) == 1:
            # segments intersect
            if (event.start == above_event.start
                    or event.end == above_event.end):
                # segments intersect at an endpoint of both line segments
                return 0
            point, = intersections
            if event.start != point and event.end != point:
                self.divide_segment(event, point)
            if above_event.start != point and above_event.end != point:
                self.divide_segment(above_event, point)
            return 1
        # segments overlap
        if event.from_left is above_event.from_left:
            raise ValueError('Edges of the same polygon should not overlap.')

        sorted_events = []
        starts_equal = event.start == above_event.start
        if starts_equal:
            sorted_events.append(None)
        elif EventsQueueKey(event) > EventsQueueKey(above_event):
            sorted_events.append(above_event)
            sorted_events.append(event)
        else:
            sorted_events.append(event)
            sorted_events.append(above_event)

        ends_equal = event.end == above_event.end
        if ends_equal:
            sorted_events.append(None)
        elif (EventsQueueKey(event.complement)
              > EventsQueueKey(above_event.complement)):
            sorted_events.append(above_event.complement)
            sorted_events.append(event.complement)
        else:
            sorted_events.append(event.complement)
            sorted_events.append(above_event.complement)

        if starts_equal:
            # both line segments are equal or share the left endpoint
            event.edge_type = EdgeType.NON_CONTRIBUTING
            above_event.edge_type = (
                EdgeType.SAME_TRANSITION
                if event.in_out is above_event.in_out
                else EdgeType.DIFFERENT_TRANSITION)
            if not ends_equal:
                self.divide_segment(sorted_events[2].complement,
                                    sorted_events[1].start)
            return 2
        elif ends_equal:
            # the line segments share the right endpoint
            self.divide_segment(sorted_events[0], sorted_events[1].start)
            return 3
        else:
            self.divide_segment(sorted_events[0]
                                # one line segment includes the other one
                                if (sorted_events[0]
                                    is sorted_events[3].complement)
                                # no line segment includes the other one
                                else sorted_events[1],
                                sorted_events[2].start)
            self.divide_segment(sorted_events[0], sorted_events[1].start)
            return 3

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = Event(False, point, event.complement, event.from_left,
                           EdgeType.NORMAL)
        right_event = Event(True, point, event, event.from_left,
                            EdgeType.NORMAL)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)


class Difference(Operation):
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

    def in_result(self, event: Event) -> bool:
        edge_type = event.edge_type
        return (edge_type is EdgeType.NORMAL
                and event.from_left is event.other_in_out
                or edge_type is EdgeType.DIFFERENT_TRANSITION)


class Intersection(Operation):
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


class SymmetricDifference(Operation):
    def in_result(self, event: Event) -> bool:
        return event.edge_type is EdgeType.NORMAL


class Union(Operation):
    def in_result(self, event: Event) -> bool:
        edge_type = event.edge_type
        return (edge_type is EdgeType.NORMAL and event.other_in_out
                or edge_type is EdgeType.SAME_TRANSITION)


def compute(operation: Type[Operation],
            left: Multipolygon,
            right: Multipolygon,
            *,
            accurate: bool) -> Multipolygon:
    """
    Returns result of given operation using optimizations for degenerate cases.

    :param operation: type of operation to perform.
    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: result of operation on operands.
    """
    if not (left or right):
        return []
    elif not (left and right):
        # at least one of the arguments is empty
        if operation is Difference:
            return left
        elif operation is Intersection:
            return []
        else:
            return left or right
    left_x_min, left_x_max, left_y_min, left_y_max = to_bounding_box(left)
    right_x_min, right_x_max, right_y_min, right_y_max = to_bounding_box(right)
    if (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min):
        # the bounding boxes do not overlap
        if operation is Difference:
            return left
        elif operation is Intersection:
            return []
        else:
            result = left + right
            result.sort(key=to_first_boundary_vertex)
            return result
    if (accurate
            and not issubclass(to_multipolygon_base(left + right), Rational)):
        left, right = (to_rational_multipolygon(left),
                       to_rational_multipolygon(right))
    return operation(left, right).compute()


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
        if not are_internal[index]:
            result.append((contour, [contours[hole_index]
                                     for hole_index in holes[index]]))
        else:
            # hole of a hole is an external polygon
            result.extend((contours[hole_index],
                           [contours[hole_hole_index]
                            for hole_hole_index in holes[hole_index]])
                          for hole_index in holes[index])
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
    for index in range(len(contour)):
        while (max(index, 2) < len(contour)
               and contour[index - 1] not in self_intersections
               and (to_orientation(contour[index - 2], contour[index - 1],
                                   contour[index])
                    is Orientation.COLLINEAR)):
            del contour[index - 1]


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
    while result > original_index and processed[result]:
        result -= 1
    return result
