from abc import (ABC,
                 abstractmethod)
from collections import defaultdict
from enum import (IntEnum,
                  unique)
from fractions import Fraction
from functools import partial
from numbers import (Rational,
                     Real)
from reprlib import recursive_repr
from typing import (Callable,
                    List,
                    Optional,
                    cast)

from dendroid import red_black
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from clipping.hints import (Coordinate,
                            Multipolygon,
                            Point,
                            Polygon,
                            Segment)
from clipping.utils import (Orientation,
                            non_real_base_orientator,
                            real_base_orientator,
                            to_bounding_box,
                            to_irrational_intersections,
                            to_multipolygon_base,
                            to_multipolygon_contours,
                            to_rational_intersections,
                            to_segments)


class _EnumBase(IntEnum):
    def __repr__(self) -> str:
        return type(self).__qualname__ + '.' + self.name


@unique
class EdgeType(_EnumBase):
    NORMAL = 0
    NON_CONTRIBUTING = 1
    SAME_TRANSITION = 2
    DIFFERENT_TRANSITION = 3


@unique
class OperationKind(_EnumBase):
    INTERSECTION = 0
    UNION = 1
    DIFFERENCE = 2
    XOR = 3


class Event(ABC):
    __slots__ = ('is_left_endpoint', 'start', 'complement', 'from_left',
                 'edge_type', 'in_out', 'other_in_out', 'in_result',
                 'result_in_out', 'position', 'contour_id',
                 'below_in_result_event')

    def __init__(self,
                 is_left_endpoint: bool,
                 start: Point,
                 complement: Optional['Event'],
                 from_left: bool,
                 edge_type: EdgeType,
                 in_out: bool = False,
                 other_in_out: bool = False,
                 in_result: bool = False,
                 result_in_out: bool = False,
                 position: int = 0,
                 contour_id: int = 0,
                 below_in_result_event: Optional['Event'] = None) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.start = start
        self.complement = complement
        self.from_left = from_left
        self.edge_type = edge_type
        self.in_out = in_out
        self.other_in_out = other_in_out
        self.in_result = in_result
        self.result_in_out = result_in_out
        self.position = position
        self.contour_id = contour_id
        self.below_in_result_event = below_in_result_event

    __repr__ = recursive_repr()(generate_repr(__init__))

    @staticmethod
    @abstractmethod
    def to_orientation(first_ray_point: Point,
                       vertex: Point,
                       second_ray_point: Point) -> Orientation:
        """
        Calculates orientation of angle built from points.
        """

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def is_vertical(self) -> bool:
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def is_above(self, point: Point) -> bool:
        return not self.is_below(point)

    def is_below(self, point: Point) -> bool:
        return (self.to_orientation(self.start, point, self.end)
                is (Orientation.COUNTERCLOCKWISE
                    if self.is_left_endpoint
                    else Orientation.CLOCKWISE))


class RealEvent(Event):
    to_orientation = staticmethod(real_base_orientator)


class NonRealEvent(Event):
    to_orientation = staticmethod(non_real_base_orientator)


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'EventsQueueKey') -> bool:
        return (self.event == other.event
                if isinstance(other, EventsQueueKey)
                else NotImplemented)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        if not isinstance(other, EventsQueueKey):
            return NotImplemented
        event, other_event = self.event, other.event
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        elif start_y != other_start_y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return not event.is_left_endpoint
        # same start, both events are left endpoints
        # or both are right endpoints
        elif (event.to_orientation(event.start, other_event.end, event.end)
              is not Orientation.COLLINEAR):
            # the event associate to the bottom segment is processed first
            return not event.is_above(other_event.end)
        else:
            return event.from_left > other_event.from_left


class SweepLineKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'SweepLineKey') -> bool:
        return (self.event == other.event
                if isinstance(other, SweepLineKey)
                else NotImplemented)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        if not isinstance(other, SweepLineKey):
            return NotImplemented
        if self is other:
            return False
        event, other_event = self.event, other.event
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        if (event.to_orientation(event.start, other_event.start, event.end)
                is event.to_orientation(event.start, other_event.end,
                                        event.end)
                is Orientation.COLLINEAR):
            # segments are collinear
            return (EventsQueueKey(event) > EventsQueueKey(other_event)
                    if event.from_left is other_event.from_left
                    else event.from_left)
        # segments are not collinear
        elif event.start == other_event.start:
            # same left endpoint, use the right endpoint to sort
            return event.is_below(other_event.end)
        # different left endpoint, use the left endpoint to sort
        elif start_x == other_start_x:
            return start_y < other_start_y
        elif EventsQueueKey(event) > EventsQueueKey(other_event):
            # has the line segment associated to `self` been inserted
            # into sweep line after the line segment associated to `other`?
            return other_event.is_above(event.start)
        else:
            # the line segment associated to `other` has been inserted
            # into sweep line after the line segment associated to `self`
            return event.is_below(other_event.start)


SweepLine = cast(Callable[[], red_black.Tree[Event]],
                 partial(red_black.tree,
                         key=SweepLineKey))
EventsQueue = cast(Callable[[], PriorityQueue[Event]],
                   partial(PriorityQueue,
                           key=EventsQueueKey))


class Operation:
    def __init__(self,
                 left: Multipolygon,
                 right: Multipolygon,
                 kind: OperationKind) -> None:
        self.left = left
        self.right = right
        self.kind = kind
        base = to_multipolygon_base(left)
        self._event_factory = (RealEvent
                               if issubclass(base, Real)
                               else NonRealEvent)
        self._intersections_seeker = (to_rational_intersections
                                      if issubclass(base, Rational)
                                      else partial(to_irrational_intersections,
                                                   base))
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    def compute(self) -> Multipolygon:
        return self._try_trivial() or self._try_non_trivial()

    def _try_trivial(self) -> Multipolygon:
        left_x_min, left_x_max, left_y_min, left_y_max = to_bounding_box(
                self.left)
        right_x_min, right_x_max, right_y_min, right_y_max = to_bounding_box(
                self.right)
        if (left_x_min > right_x_max or right_x_min > left_x_max
                or left_y_min > right_y_max or right_y_min > left_y_max):
            # the bounding boxes do not overlap
            if self.kind is OperationKind.DIFFERENCE:
                return self.left
            elif (self.kind is OperationKind.UNION
                  or self.kind is OperationKind.XOR):
                return self.left + self.right
        return []

    def _try_non_trivial(self) -> Multipolygon:
        return _connect_edges(self.sweep())

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        is_intersection = self.kind is OperationKind.INTERSECTION
        is_difference = self.kind is OperationKind.DIFFERENCE
        left_x_max, right_x_max = _to_x_max(self.left), _to_x_max(self.right)
        min_max_x = min(left_x_max, right_x_max)
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if (is_intersection and start_x > min_max_x
                    or is_difference and start_x > left_x_max):
                break
            result.append(event)
            if event.is_left_endpoint:
                sweep_line.add(event)
                try:
                    above_event = sweep_line.next(event)
                except ValueError:
                    above_event = None
                try:
                    below_event = sweep_line.prev(event)
                except ValueError:
                    below_event = None
                self.compute_fields(event, below_event)
                if above_event is not None:
                    if self.detect_intersection(event, above_event) == 2:
                        self.compute_fields(event, below_event)
                        self.compute_fields(above_event, event)
                if below_event is not None:
                    if self.detect_intersection(below_event, event) == 2:
                        try:
                            below_below_event = sweep_line.prev(below_event)
                        except ValueError:
                            below_below_event = None
                        self.compute_fields(below_event, below_below_event)
                        self.compute_fields(event, below_event)
            else:
                event = event.complement
                if event not in sweep_line:
                    continue
                try:
                    above_event = sweep_line.next(event)
                except ValueError:
                    above_event = None
                try:
                    below_event = sweep_line.prev(event)
                except ValueError:
                    below_event = None
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self.detect_intersection(below_event, above_event)
        return result

    def fill_queue(self) -> None:
        for contour in to_multipolygon_contours(self.left):
            for segment in to_segments(contour):
                self.process_segment(segment, True)
        for contour in to_multipolygon_contours(self.right):
            for segment in to_segments(contour):
                self.process_segment(segment, False)

    def process_segment(self, segment: Segment, from_left: bool) -> None:
        start, end = sorted(segment)
        start_event = self._event_factory(True, start, None, from_left,
                                          EdgeType.NORMAL)
        end_event = self._event_factory(False, end, start_event, from_left,
                                        EdgeType.NORMAL)
        start_event.complement = end_event
        self._events_queue.push(start_event)
        self._events_queue.push(end_event)

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

    def in_result(self, event: Event) -> bool:
        edge_type = event.edge_type
        operation_kind = self.kind
        if edge_type is EdgeType.NORMAL:
            if operation_kind is OperationKind.INTERSECTION:
                return not event.other_in_out
            elif operation_kind is OperationKind.UNION:
                return event.other_in_out
            elif operation_kind is OperationKind.DIFFERENCE:
                return event.from_left is event.other_in_out
            else:
                return operation_kind is OperationKind.XOR
        elif edge_type is EdgeType.SAME_TRANSITION:
            return (operation_kind is OperationKind.INTERSECTION
                    or operation_kind is OperationKind.UNION)
        elif edge_type is EdgeType.DIFFERENT_TRANSITION:
            return operation_kind is OperationKind.DIFFERENCE
        else:
            return False

    def detect_intersection(self,
                            first_event: Event,
                            second_event: Event) -> int:
        intersections = self._intersections_seeker(first_event.segment,
                                                   second_event.segment)
        if not intersections:
            # no intersection
            return 0
        elif len(intersections) == 1:
            # segments intersect
            point, = intersections
            if (first_event.start == second_event.start
                    or first_event.end == second_event.end):
                # segments intersect at an endpoint of both line segments
                return 0
            if first_event.start != point and first_event.end != point:
                # if the intersection start is not an endpoint of le1.segment
                self.divide_segment(first_event, point)
            if second_event.start != point and second_event.end != point:
                # if the intersection start is not an endpoint of le2.segment
                self.divide_segment(second_event, point)
            return 1
        # segments overlap
        if first_event.from_left is second_event.from_left:
            raise ValueError('Edges of the same polygon should not overlap.')

        sorted_events = []
        if first_event.start == second_event.start:
            sorted_events.append(None)
        elif EventsQueueKey(first_event) > EventsQueueKey(second_event):
            sorted_events.append(second_event)
            sorted_events.append(first_event)
        else:
            sorted_events.append(first_event)
            sorted_events.append(second_event)

        if first_event.end == second_event.end:
            sorted_events.append(None)
        elif (EventsQueueKey(first_event.complement)
              > EventsQueueKey(second_event.complement)):
            sorted_events.append(second_event.complement)
            sorted_events.append(first_event.complement)
        else:
            sorted_events.append(first_event.complement)
            sorted_events.append(second_event.complement)

        if (len(sorted_events) == 2
                or len(sorted_events) == 3 and sorted_events[2]):
            # both line segments are equal or share the left endpoint
            first_event.edge_type = EdgeType.NON_CONTRIBUTING
            second_event.edge_type = (
                EdgeType.SAME_TRANSITION
                if first_event.in_out is second_event.in_out
                else EdgeType.DIFFERENT_TRANSITION)
            if len(sorted_events) == 3:
                self.divide_segment(sorted_events[2].complement,
                                    sorted_events[1].start)
            return 2
        elif len(sorted_events) == 3:
            # the line segments share the right endpoint
            self.divide_segment(sorted_events[0], sorted_events[1].start)
            return 3
        else:
            self.divide_segment(sorted_events[0], sorted_events[1].start)
            self.divide_segment(sorted_events[0]
                                # one line segment includes the other one
                                if (sorted_events[0]
                                    is sorted_events[3].complement)
                                # no line segment includes the other one
                                else sorted_events[1],
                                sorted_events[2].start)
            return 3

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = self._event_factory(True, point, event.complement,
                                         event.from_left, EdgeType.NORMAL)
        right_event = self._event_factory(False, point, event, event.from_left,
                                          EdgeType.NORMAL)
        if EventsQueueKey(left_event) > EventsQueueKey(event.complement):
            # avoid a rounding error,
            # the left event would be processed after the right event
            event.complement.is_left_endpoint = True
            left_event.is_left_endpoint = False
        event.complement, event.complement.complement = right_event, left_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)


def _to_x_max(multipolygon: Multipolygon) -> Coordinate:
    return max(x for border, _ in multipolygon for x, _ in border)


def _compute(operation_kind: OperationKind,
             left: Multipolygon,
             right: Multipolygon) -> Multipolygon:
    return Operation(left, right, operation_kind).compute()


intersect = cast(Callable[[Multipolygon, Multipolygon], Multipolygon],
                 partial(_compute, OperationKind.INTERSECTION))
unite = cast(Callable[[Multipolygon, Multipolygon], Multipolygon],
             partial(_compute, OperationKind.UNION))
subtract = cast(Callable[[Multipolygon, Multipolygon], Multipolygon],
                partial(_compute, OperationKind.DIFFERENCE))
symmetric_subtract = cast(Callable[[Multipolygon, Multipolygon], Multipolygon],
                          partial(_compute, OperationKind.XOR))


def _connect_edges(events: List[Event]) -> List[Polygon]:
    return _events_to_contours(_collect_events(events))


def _collect_events(events: List[Event]) -> List[Event]:
    result = [event
              for event in events
              if event.is_left_endpoint and event.in_result
              or not event.is_left_endpoint and event.complement.in_result]
    is_sorted = False
    while not is_sorted:
        is_sorted = True
        for index in range(len(result) - 1):
            if (EventsQueueKey(result[index])
                    > EventsQueueKey(result[index + 1])):
                result[index], result[index + 1] = (result[index + 1],
                                                    result[index])
                is_sorted = False
    for index, event in enumerate(result):
        event.position = index
        if not event.is_left_endpoint:
            event.position, event.complement.position = (
                event.complement.position, event.position)
    return result


def _events_to_contours(events: List[Event]) -> List[Polygon]:
    depth, hole_of = [], []
    processed = [False] * len(events)
    contours = []
    are_internal = defaultdict(bool)
    holes = defaultdict(list)
    for index, event in enumerate(events):
        if processed[index]:
            continue

        is_internal = False
        contour_id = len(contours)
        depth.append(0)
        hole_of.append(-1)
        if event.below_in_result_event is not None:
            lower_contour_id = event.below_in_result_event.contour_id
            if not event.below_in_result_event.result_in_out:
                holes[lower_contour_id].append(contour_id)
                hole_of[contour_id] = lower_contour_id
                depth[contour_id] = depth[lower_contour_id] + 1
                is_internal = True
            elif are_internal[lower_contour_id]:
                lower_contour_hole_id = hole_of[lower_contour_id]
                holes[lower_contour_hole_id].append(contour_id)
                hole_of[contour_id] = lower_contour_hole_id
                depth[contour_id] = depth[lower_contour_id]
                is_internal = True
        are_internal[contour_id] = is_internal

        position = index
        initial = event.start
        contour = [initial]
        while position >= index:
            event = events[position]
            if event.end == initial:
                break
            processed[position] = True
            if event.is_left_endpoint:
                event.result_in_out = False
                event.contour_id = contour_id
            else:
                event.complement.result_in_out = True
                event.complement.contour_id = contour_id
            position = event.position
            processed[position] = True
            contour.append(events[position].start)
            position = _to_next_position(position, events, processed, index)
        position = index if position == -1 else position
        event = events[position]
        processed[position] = processed[event.position] = True
        event.complement.result_in_out = True
        event.complement.contour_id = contour_id

        if depth[contour_id] & 1:
            contour.reverse()

        contours.append(contour)
    return [(contour, [contours[hole_index]
                       for hole_index in holes[index]])
            for index, contour in enumerate(contours)]


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
