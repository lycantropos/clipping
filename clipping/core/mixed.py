from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (List,
                    Optional,
                    Union)

from reprit.base import generate_repr

from clipping.hints import (Mix,
                            Multipoint,
                            Multipolygon,
                            Multisegment)
from . import bounding_box
from .event import MixedEvent as Event
from .events_queue import (BinaryEventsQueueKey as EventsQueueKey,
                           MixedBinaryEventsQueue as EventsQueue)
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

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        events_queue.register_segments(self.multisegment, True)
        for polygon in self.multipolygon:
            events_queue.register_segments(
                    polygon_to_oriented_segments(polygon), False)

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
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)
        elif event not in sweep_line:
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
        events_queue = self._events_queue
        sweep_line = SweepLine()
        left_x_max = to_multisegment_x_max(self.multisegment)
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > left_x_max:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
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
        events_queue = self._events_queue
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
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
        events_queue = self._events_queue
        sweep_line = SweepLine()
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            if not event.is_right_endpoint:
                result.append(event)
        return result
