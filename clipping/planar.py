"""
Boolean operations on polygons/multipolygons in the plane.

Based on algorithm by F. Martinez et al.

Time complexity:
    ``O((len(left) + len(right) + len(intersections)) * log (len(left) \
+ len(right)))``
Memory complexity:
    ``O(len(left) + len(right) + len(intersections))``
Reference:
    https://doi.org/10.1016/j.advengsoft.2013.04.004
    http://www4.ujaen.es/~fmartin/bool_op.html

########
Glossary
########

*Point* --- a pair of real numbers.

*Segment* (or *line segment*) --- a pair of unequal points.

*Contour* --- a sequence of points (called contour's vertices)
such that line segments formed by pairs of consecutive points
(including the last-first point pair)
do not overlap each other.

*Polygon* --- pair of contour (called polygon's border)
and possibly empty sequence of non-overlapping contours
which lie within the border (called polygon's holes).

*Multipolygon* --- possibly empty sequence of non-overlapping polygons.
"""
from collections import defaultdict
from enum import (IntEnum,
                  unique)
from functools import partial
from numbers import Rational
from reprlib import recursive_repr
from typing import (Callable,
                    List,
                    Optional,
                    cast)

from bentley_ottmann import linear
from bentley_ottmann.angular import (Orientation,
                                     to_orientation)
from dendroid import red_black
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .hints import (Coordinate,
                    Multipolygon,
                    Point,
                    Polygon,
                    Segment)
from .utils import (shrink_collinear_vertices,
                    to_bounding_box,
                    to_first_boundary_vertex,
                    to_multipolygon_base,
                    to_multipolygon_contours,
                    to_rational_multipolygon,
                    to_segments)


@unique
class EdgeType(IntEnum):
    __doc__ = ''

    NORMAL = 0
    NON_CONTRIBUTING = 1
    SAME_TRANSITION = 2
    DIFFERENT_TRANSITION = 3


@unique
class OperationKind(IntEnum):
    __doc__ = ''

    INTERSECTION = 0
    UNION = 1
    DIFFERENCE = 2
    XOR = 3


class Event:
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
                 contour_id: Optional[int] = None,
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

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def is_vertical(self) -> bool:
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def is_horizontal(self) -> bool:
        _, start_y = self.start
        _, end_y = self.end
        return start_y == end_y

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def y_at(self, x: Coordinate) -> Coordinate:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            start_x, start_y = self.start
            if x == start_x:
                return start_y
            end_x, end_y = self.end
            if x == end_x:
                return end_y
            (_, result), = linear.find_intersections(self.segment,
                                                     ((x, start_y),
                                                      (x, end_y)))
            return result


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

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
        else:
            other_end_orientation = to_orientation(event.start,
                                                   other_event.end,
                                                   event.end)
            # the lowest segment is processed first
            if other_end_orientation is Orientation.COLLINEAR:
                _, end_y = event.end
                _, other_end_y = other_event.end
                if end_y != other_end_y:
                    return end_y < other_end_y
                else:
                    # segments are equal
                    return event.from_left > other_event.from_left
            else:
                return other_end_orientation is Orientation.COUNTERCLOCKWISE


class SweepLine:
    def __init__(self, *events: Event,
                 current_x: Optional[Coordinate] = None) -> None:
        self.current_x = current_x
        self._tree = red_black.tree(*events,
                                    key=cast(Callable[[Event], SweepLineKey],
                                             partial(SweepLineKey, self)))

    __repr__ = generate_repr(__init__)

    @property
    def events(self) -> List[Event]:
        return list(self._tree)

    def __contains__(self, event: Event) -> bool:
        return event in self._tree

    def move_to(self, x: Coordinate) -> None:
        self.current_x = x

    def add(self, event: Event) -> None:
        self._tree.add(event)

    def remove(self, event: Event) -> None:
        self._tree.remove(event)

    def above(self, event: Event) -> Event:
        return self._tree.next(event)

    def below(self, event: Event) -> Event:
        return self._tree.prev(event)


class SweepLineKey:
    __slots__ = ('sweep_line', 'event')

    def __init__(self, sweep_line: SweepLine, event: Event) -> None:
        self.sweep_line = sweep_line
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        if not isinstance(other, SweepLineKey):
            return NotImplemented
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        end_x, end_y = event.end
        other_end_x, other_end_y = other_event.end
        other_start_orientation = to_orientation(end, start, other_start)
        other_end_orientation = to_orientation(end, start, other_end)
        start_orientation = to_orientation(other_end, other_start, start)
        end_orientation = to_orientation(other_end, other_start, end)
        if other_start_orientation is other_end_orientation:
            if other_start_orientation is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return other_start_orientation is Orientation.COUNTERCLOCKWISE
            # segments are collinear
            elif event.from_left is not other_event.from_left:
                return event.from_left
            elif start_x == other_start_x:
                if start_y != other_start_y:
                    # segments are vertical
                    return start_y < other_start_y
                else:
                    # segments have same start
                    return end_y < other_end_y
            elif start_y != other_start_y:
                return start_y < other_start_y
            else:
                # segments are horizontal
                return start_x < other_start_x
        elif start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif event.is_vertical:
            return start_orientation is Orientation.CLOCKWISE
        elif other_event.is_vertical:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
        elif other_end_orientation is Orientation.COLLINEAR:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            current_x = self.sweep_line.current_x
            return event.y_at(current_x) < other_event.y_at(current_x)


EventsQueue = cast(Callable[[], PriorityQueue[Event]],
                   partial(PriorityQueue,
                           key=EventsQueueKey))


class Operation:
    __slots__ = ('left', 'right', 'kind', '_events_queue')

    def __init__(self,
                 left: Multipolygon,
                 right: Multipolygon,
                 kind: OperationKind) -> None:
        self.left = left
        self.right = right
        self.kind = kind
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    def compute(self) -> Multipolygon:
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
            sweep_line.move_to(start_x)
            result.append(event)
            if event.is_left_endpoint:
                sweep_line.add(event)
                try:
                    above_event = sweep_line.above(event)
                except ValueError:
                    above_event = None
                try:
                    below_event = sweep_line.below(event)
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
                            below_below_event = sweep_line.below(below_event)
                        except ValueError:
                            below_below_event = None
                        self.compute_fields(below_event, below_below_event)
                        self.compute_fields(event, below_event)
            else:
                event = event.complement
                if event not in sweep_line:
                    continue
                try:
                    above_event = sweep_line.above(event)
                except ValueError:
                    above_event = None
                try:
                    below_event = sweep_line.below(event)
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
        start_event = Event(True, start, None, from_left, EdgeType.NORMAL)
        end_event = Event(False, end, start_event, from_left, EdgeType.NORMAL)
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
        intersections = linear.find_intersections(first_event.segment,
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
        left_event = Event(True, point, event.complement, event.from_left,
                           EdgeType.NORMAL)
        right_event = Event(False, point, event, event.from_left,
                            EdgeType.NORMAL)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)


def _to_x_max(multipolygon: Multipolygon) -> Coordinate:
    return max(x for border, _ in multipolygon for x, _ in border)


def _compute(operation_kind: OperationKind,
             left: Multipolygon,
             right: Multipolygon,
             *,
             accurate: bool = True) -> Multipolygon:
    if not (left or right):
        return []
    elif not (left and right):
        # at least one of the arguments is empty
        if operation_kind is OperationKind.DIFFERENCE:
            return left
        if (operation_kind is OperationKind.UNION
                or operation_kind is OperationKind.XOR):
            return left or right
        return []
    left_x_min, left_x_max, left_y_min, left_y_max = to_bounding_box(left)
    right_x_min, right_x_max, right_y_min, right_y_max = to_bounding_box(right)
    if (left_x_min > right_x_max or left_x_max < right_x_min
            or left_y_min > right_y_max or left_y_max < right_y_min):
        # the bounding boxes do not overlap
        if operation_kind is OperationKind.DIFFERENCE:
            return left
        elif (operation_kind is OperationKind.UNION
              or operation_kind is OperationKind.XOR):
            result = left + right
            result.sort(key=to_first_boundary_vertex)
            return result
        return []
    if (accurate
            and not issubclass(to_multipolygon_base(left + right), Rational)):
        left, right = (to_rational_multipolygon(left),
                       to_rational_multipolygon(right))
    return Operation(left, right, operation_kind).compute()


def intersect(left: Multipolygon,
              right: Multipolygon,
              *,
              accurate: bool = True) -> Multipolygon:
    """
    Returns intersection of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: intersection of operands.

    >>> intersect([], [])
    []
    >>> intersect([([(0, 0), (1, 0), (0, 1)], [])], [])
    []
    >>> intersect([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> intersect([([(0, 0), (1, 0), (0, 1)], [])],
    ...           [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _compute(OperationKind.INTERSECTION, left, right,
                    accurate=accurate)


def unite(left: Multipolygon,
          right: Multipolygon,
          *,
          accurate: bool = True) -> Multipolygon:
    """
    Returns union of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: union of operands.

    >>> unite([], [])
    []
    >>> unite([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> unite([([(0, 0), (1, 0), (0, 1)], [])],
    ...       [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    """
    return _compute(OperationKind.UNION, left, right,
                    accurate=accurate)


def subtract(minuend: Multipolygon,
             subtrahend: Multipolygon,
             *,
             accurate: bool = True) -> Multipolygon:
    """
    Returns difference of multipolygons.

    :param minuend: multipolygon from which to subtract.
    :param subtrahend: multipolygon which to subtract.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: difference between minuend and subtrahend.

    >>> subtract([], [])
    []
    >>> subtract([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> subtract([], [([(0, 0), (1, 0), (0, 1)], [])])
    []
    >>> subtract([([(0, 0), (1, 0), (0, 1)], [])],
    ...          [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _compute(OperationKind.DIFFERENCE, minuend, subtrahend,
                    accurate=accurate)


def symmetric_subtract(left: Multipolygon,
                       right: Multipolygon,
                       *,
                       accurate: bool = True) -> Multipolygon:
    """
    Returns symmetric difference of multipolygons.

    :param left: left operand.
    :param right: right operand.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: symmetric difference of operands.

    >>> symmetric_subtract([], [])
    []
    >>> symmetric_subtract([([(0, 0), (1, 0), (0, 1)], [])], [])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract([], [([(0, 0), (1, 0), (0, 1)], [])])
    [([(0, 0), (1, 0), (0, 1)], [])]
    >>> symmetric_subtract([([(0, 0), (1, 0), (0, 1)], [])],
    ...                    [([(0, 0), (1, 0), (0, 1)], [])])
    []
    """
    return _compute(OperationKind.XOR, left, right,
                    accurate=accurate)


def _connect_edges(events: List[Event]) -> List[Polygon]:
    return _events_to_contours(_collect_events(events))


def _collect_events(events: List[Event]) -> List[Event]:
    result = sorted(
            [event
             for event in events
             if event.is_left_endpoint and event.in_result
             or not event.is_left_endpoint and event.complement.in_result],
            key=EventsQueueKey)
    for index, event in enumerate(result):
        event.position = index
        if not event.is_left_endpoint:
            event.position, event.complement.position = (
                event.complement.position, event.position)
    return result


def _events_to_contours(events: List[Event]) -> List[Polygon]:
    depth, hole_of = defaultdict(int), []
    processed = [False] * len(events)
    contours = []
    are_internal = defaultdict(bool)
    holes = defaultdict(list)
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

        shrink_collinear_vertices(contour)
        if len(contour) < 3:
            continue

        contour_id = len(contours)

        is_internal = False
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

        for step in steps:
            if step.is_left_endpoint:
                step.result_in_out = False
                step.contour_id = contour_id
            else:
                step.complement.result_in_out = True
                step.complement.contour_id = contour_id
        last_event.complement.result_in_out = True
        last_event.complement.contour_id = contour_id

        if depth[contour_id] & 1:
            # holes will be in clockwise order
            contour.reverse()

        contours.append(contour)
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
