from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Union)

from reprit.base import generate_repr
from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_relationship)

from clipping.hints import (Mix,
                            Multipoint,
                            Multipolygon,
                            Multisegment,
                            Point,
                            Segment)
from . import bounding_box
from .event import MixedEvent as Event
from .events_queue import (BinaryEventsQueue as EventsQueue,
                           BinaryEventsQueueKey as EventsQueueKey)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    polygon_to_oriented_segments,
                    to_mixed_base,
                    to_multipolygon_x_max,
                    to_multisegment_x_max,
                    to_rational_multipolygon,
                    to_rational_multisegment)


class Operation(ABC):
    __slots__ = 'multisegment', 'multipolygon', 'accurate', '_events_queue'

    def __init__(self,
                 multisegment: Multisegment,
                 multipolygon: Multipolygon,
                 accurate: bool) -> None:
        """
        Initializes operation.

        :param multisegment: left operand.
        :param multipolygon: right operand.
        :param accurate:
            flag that tells whether to use slow but more accurate arithmetic
            for floating point numbers.
        """
        self.multisegment = multisegment
        self.multipolygon = multipolygon
        self.accurate = accurate
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union[Multisegment, Mix]:
        """
        Computes result of the operation.
        """

    def compute_fields(self, event: Event,
                       below_event: Optional[Event]) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_left
                                                is below_event.from_left)
                                            else below_event.interior_to_left)
        event.in_result = self.in_result(event)

    def detect_intersection(self, below_event: Event, event: Event) -> bool:
        below_segment, segment = below_event.segment, event.segment
        relationship = segments_relationship(below_segment, segment)
        if relationship is SegmentsRelationship.OVERLAP:
            # segments overlap
            if below_event.from_left is event.from_left:
                raise ValueError('Edges of the {geometry} '
                                 'should not overlap.'
                                 .format(geometry=('multisegment'
                                                   if event.from_left
                                                   else 'multipolygon')))
            event.is_overlap = below_event.is_overlap = True
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
        self.register_segments(self.multisegment, True)
        for polygon in self.multipolygon:
            self.register_segments(polygon_to_oriented_segments(polygon),
                                   False)

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def normalize_operands(self) -> None:
        multisegment, multipolygon = self.multisegment, self.multipolygon
        if (self.accurate
                and not issubclass(to_mixed_base(multisegment, multipolygon),
                                   Rational)):
            self.multisegment, self.multipolygon = (
                to_rational_multisegment(multisegment),
                to_rational_multipolygon(multipolygon))

    def process_event(self, event: Event, sweep_line: SweepLine) -> None:
        if event.is_right_endpoint:
            event = event.complement
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self.detect_intersection(below_event, above_event)
        elif event not in sweep_line:
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
            interior_to_left = True
            if start > end:
                start, end = end, start
                interior_to_left = False
            start_event = Event(False, start, None, from_left,
                                interior_to_left)
            end_event = Event(True, end, start_event, from_left,
                              interior_to_left)
            start_event.complement = end_event
            events_queue.push(start_event)
            events_queue.push(end_event)

    @abstractmethod
    def sweep(self) -> List[Event]:
        """
        Sweeps through plane returning processed events.
        """


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.multisegment and self.multipolygon):
            return self.multisegment
        multisegment_bounding_box = (bounding_box
                                     .from_multisegment(self.multisegment))
        if bounding_box.disjoint_with(
                multisegment_bounding_box,
                bounding_box.from_multipolygon(self.multipolygon)):
            return self.multisegment
        self.multipolygon = bounding_box.to_coupled_polygons(
                multisegment_bounding_box, self.multipolygon)
        if not self.multipolygon:
            return self.multisegment
        self.normalize_operands()
        return [event.segment for event in self.sweep() if event.in_result]

    def in_result(self, event: Event) -> bool:
        return event.from_left and event.outside

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        left_x_max = to_multisegment_x_max(self.multisegment)
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
        if not (self.multisegment and self.multipolygon):
            return []
        multisegment_bounding_box = (bounding_box
                                     .from_multisegment(self.multisegment))
        multipolygon_bounding_box = (bounding_box
                                     .from_multipolygon(self.multipolygon))
        if bounding_box.disjoint_with(multisegment_bounding_box,
                                      multipolygon_bounding_box):
            return []
        self.multisegment = bounding_box.to_intersecting_segments(
                multipolygon_bounding_box, self.multisegment)
        self.multipolygon = bounding_box.to_intersecting_polygons(
                multisegment_bounding_box, self.multipolygon)
        if not (self.multisegment and self.multipolygon):
            return []
        self.normalize_operands()
        return [event.segment for event in self.sweep() if event.in_result]

    def in_result(self, event: Event) -> bool:
        return event.from_left and not event.outside

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            if not event.is_right_endpoint:
                result.append(event)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        if not (self.multisegment and self.multipolygon):
            return [], [], []
        multisegment_bounding_box = (bounding_box
                                     .from_multisegment(self.multisegment))
        multipolygon_bounding_box = (bounding_box
                                     .from_multipolygon(self.multipolygon))
        if bounding_box.disjoint_with(multisegment_bounding_box,
                                      multipolygon_bounding_box):
            return [], [], []
        self.multisegment = bounding_box.to_intersecting_segments(
                multipolygon_bounding_box, self.multisegment)
        self.multipolygon = bounding_box.to_intersecting_polygons(
                multisegment_bounding_box, self.multipolygon)
        if not (self.multisegment and self.multipolygon):
            return [], [], []
        self.normalize_operands()
        events = sorted(self.sweep(),
                        key=EventsQueueKey)
        multipoint = []  # type: Multipoint
        border_multisegment = []  # type: Multisegment
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if (all(not (event.in_result or event.is_right_endpoint
                         and event.complement.in_result)
                    for event in same_start_events)
                    and not all_equal(event.from_left
                                      for event in same_start_events)):
                multipoint.append(start)
        inside_multisegment = [event.segment
                               for event in events
                               if event.in_result]
        return multipoint, border_multisegment + inside_multisegment, []

    def in_result(self, event: Event) -> bool:
        return event.from_left and not event.outside

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result
