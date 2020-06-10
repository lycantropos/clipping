from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (List,
                    Union as Union_)

from reprit.base import generate_repr
from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from clipping.hints import (Mix,
                            Multipoint,
                            Multisegment,
                            Point,
                            Segment)
from .event import LinearEvent as Event
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .sweep_line import SweepLine
from .utils import (all_equal,
                    are_bounding_boxes_disjoint,
                    flatten,
                    sort_pair,
                    to_bounding_box,
                    to_multisegment_base,
                    to_multisegment_x_max,
                    to_rational_multisegment)


class Operation(ABC):
    __slots__ = 'left', 'right', 'accurate', '_events_queue'

    def __init__(self,
                 left: Multisegment,
                 right: Multisegment,
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

    def are_operands_bounding_boxes_disjoint(self) -> bool:
        return are_bounding_boxes_disjoint(
                to_bounding_box(flatten(self.left)),
                to_bounding_box(flatten(self.right)))

    @abstractmethod
    def compute(self) -> Union_[Multisegment, Mix]:
        """
        Computes result of the operation.
        """

    def detect_intersection(self, below_event: Event, event: Event) -> None:
        below_segment, segment = below_event.segment, event.segment
        relationship = segments_relationship(below_segment, segment)
        if relationship is SegmentsRelationship.OVERLAP:
            # segments overlap
            if below_event.from_left is event.from_left:
                raise ValueError('Segments of the same multisegment '
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
                if not ends_equal:
                    self.divide_segment(end_max.complement, end_min.start)
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

    def divide_segment(self, event: Event, point: Point) -> None:
        left_event = Event(False, point, event.complement, event.from_left)
        right_event = Event(True, point, event, event.from_left)
        event.complement.complement, event.complement = left_event, right_event
        self._events_queue.push(left_event)
        self._events_queue.push(right_event)

    def fill_queue(self) -> None:
        for segment in self.left:
            self.register_segment(segment, True)
        for segment in self.right:
            self.register_segment(segment, False)

    def normalize_operands(self) -> None:
        left, right = self.left, self.right
        if (self.accurate
                and not issubclass(to_multisegment_base(left + right),
                                   Rational)):
            self.left, self.right = (to_rational_multisegment(left),
                                     to_rational_multisegment(right))

    def process_event(self, event: Event, sweep_line: SweepLine) -> None:
        start_x, _ = event.start
        sweep_line.move_to(start_x)
        if event.is_right_endpoint:
            event = event.complement
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self.detect_intersection(below_event, above_event)
        else:
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            if above_event is not None:
                self.detect_intersection(event, above_event)
            if below_event is not None:
                self.detect_intersection(below_event, event)

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
            event = self._events_queue.pop()
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if (not (self.left and self.right)
                or self.are_operands_bounding_boxes_disjoint()):
            return self.left
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if all(event.from_left for event in events))

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        left_x_max = to_multisegment_x_max(self.left)
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > left_x_max:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if (not (self.left and self.right)
                or self.are_operands_bounding_boxes_disjoint()):
            return []
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if not all_equal(event.from_left for event in events))

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.left),
                        to_multisegment_x_max(self.right))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        if (not (self.left and self.right)
                or self.are_operands_bounding_boxes_disjoint()):
            return [], [], []
        self.normalize_operands()
        multipoint = []  # type: Multipoint
        multisegment = []  # type: Multisegment
        for start, same_start_events in groupby(sorted(self.sweep(),
                                                       key=event_to_segment),
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not all_equal(event.from_left for event in same_start_events):
                no_segment_found = True
                for event, next_event in zip(same_start_events,
                                             same_start_events[1:]):
                    if (event.from_left is not next_event.from_left
                            and event.segment == next_event.segment):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            multisegment.append(event.segment)
                if no_segment_found:
                    multipoint.append(start)
        return multipoint, multisegment, []

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.left),
                        to_multisegment_x_max(self.right))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return self.left or self.right
        elif self.are_operands_bounding_boxes_disjoint():
            result = self.left + self.right
            result.sort()
            return result
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if all_equal(event.from_left for event in events))


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return self.left or self.right
        elif self.are_operands_bounding_boxes_disjoint():
            result = self.left + self.right
            result.sort()
            return result
        self.normalize_operands()
        return sorted(segment
                      for segment, _ in groupby(self.sweep(),
                                                key=event_to_segment))


event_to_segment = attrgetter('segment')
