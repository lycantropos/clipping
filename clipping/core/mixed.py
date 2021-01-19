from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Union)

from ground.base import Context
from ground.hints import Point
from reprit.base import generate_repr

from . import bounding
from .event import (MixedEvent as Event,
                    event_to_segment_endpoints)
from .events_queue import MixedBinaryEventsQueue as EventsQueue
from .hints import (Mix,
                    Multipolygon,
                    Multisegment)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    endpoints_to_multisegment,
                    multisegment_to_endpoints,
                    points_to_multipoint,
                    polygon_to_oriented_edges_endpoints,
                    to_multipolygon_x_max,
                    to_multisegment_x_max)


class Operation(ABC):
    __slots__ = 'context', 'multisegment', 'multipolygon', '_events_queue'

    def __init__(self,
                 multisegment: Multisegment,
                 multipolygon: Multipolygon,
                 context: Context) -> None:
        """
        Initializes operation.

        :param multisegment: left operand.
        :param multipolygon: right operand.
        :param context: operation context.
        """
        self.context, self.multisegment, self.multipolygon = (
            context, multisegment, multipolygon)
        self._events_queue = EventsQueue(context)

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
        events_queue.register(multisegment_to_endpoints(self.multisegment),
                              True)
        for polygon in self.multipolygon:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon,
                                                        context=self.context),
                    False)

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def normalize_operands(self) -> None:
        pass

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
        multisegment_box = bounding.from_multisegment(self.multisegment,
                                                      context=self.context)
        if bounding.disjoint_with(
                multisegment_box,
                bounding.from_multipolygon(self.multipolygon,
                                           context=self.context)):
            return self.multisegment
        self.multipolygon = bounding.to_coupled_polygons(multisegment_box,
                                                         self.multipolygon,
                                                         context=self.context)
        if not self.multipolygon:
            return self.multisegment
        self.normalize_operands()
        return endpoints_to_multisegment([event_to_segment_endpoints(event)
                                          for event in self.sweep()
                                          if event.in_result],
                                         context=self.context)

    def in_result(self, event: Event) -> bool:
        return event.from_left and event.outside

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        left_x_max = to_multisegment_x_max(self.multisegment)
        while events_queue:
            event = events_queue.pop()
            if left_x_max < event.start.x:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        if not (self.multisegment and self.multipolygon):
            return points_to_multipoint([], context=self.context), [], []
        multisegment_box = bounding.from_multisegment(self.multisegment,
                                                      context=self.context)
        multipolygon_box = bounding.from_multipolygon(self.multipolygon,
                                                      context=self.context)
        if bounding.disjoint_with(multisegment_box, multipolygon_box):
            return points_to_multipoint([],
                                        context=self.context), [], []
        self.multisegment = bounding.to_intersecting_segments(
                multipolygon_box, self.multisegment,
                context=self.context)
        self.multipolygon = bounding.to_intersecting_polygons(
                multisegment_box, self.multipolygon,
                context=self.context)
        if not (self.multisegment and self.multipolygon):
            return points_to_multipoint([], context=self.context), [], []
        self.normalize_operands()
        events = sorted(self.sweep(),
                        key=self._events_queue.key)
        points = []  # type: List[Point]
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if (all(not (event.in_result or event.is_right_endpoint
                         and event.complement.in_result)
                    for event in same_start_events)
                    and not all_equal(event.from_left
                                      for event in same_start_events)):
                points.append(start)
        return (points_to_multipoint(points,
                                     context=self.context),
                endpoints_to_multisegment([event_to_segment_endpoints(event)
                                           for event in events
                                           if event.in_result],
                                          context=self.context),
                [])

    def in_result(self, event: Event) -> bool:
        return event.from_left and not event.outside

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.multisegment and self.multipolygon):
            return []
        multisegment_box = bounding.from_multisegment(self.multisegment,
                                                      context=self.context)
        multipolygon_box = bounding.from_multipolygon(self.multipolygon,
                                                      context=self.context)
        if bounding.disjoint_with(multisegment_box,
                                  multipolygon_box):
            return []
        self.multisegment = bounding.to_intersecting_segments(
                multipolygon_box, self.multisegment,
                context=self.context)
        self.multipolygon = bounding.to_intersecting_polygons(
                multisegment_box, self.multipolygon,
                context=self.context)
        if not (self.multisegment and self.multipolygon):
            return []
        self.normalize_operands()
        return endpoints_to_multisegment([event_to_segment_endpoints(event)
                                          for event in self.sweep()
                                          if event.in_result],
                                         context=self.context)

    def in_result(self, event: Event) -> bool:
        return event.from_left and not event.outside

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_multisegment_x_max(self.multisegment),
                        to_multipolygon_x_max(self.multipolygon))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_right_endpoint:
                result.append(event)
        return result
