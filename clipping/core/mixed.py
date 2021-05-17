from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Union as Union_)

from ground.base import Context
from ground.hints import (Empty,
                          Mix,
                          Multipoint,
                          Multipolygon,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment)
from reprit.base import generate_repr

from . import bounding
from .event import (LeftMixedEvent as LeftEvent,
                    RightMixedEvent as RightEvent)
from .events_queue import MixedEventsQueue as EventsQueue
from .operands import (HoleyOperand,
                       LinearOperand)
from .sweep_line import BinarySweepLine as SweepLine
from .unpacking import (unpack_linear_mix,
                        unpack_points,
                        unpack_segments)
from .utils import (all_equal,
                    endpoints_to_segments,
                    polygon_to_oriented_edges_endpoints,
                    segments_to_endpoints,
                    to_endpoints,
                    to_polygons_x_max,
                    to_segments_x_max)

Event = Union_[LeftEvent, RightEvent]


class Operation(ABC):
    __slots__ = 'context', 'linear', 'shaped', '_events_queue'

    def __init__(self,
                 linear: LinearOperand,
                 shaped: HoleyOperand,
                 context: Context) -> None:
        """
        Initializes operation.

        :param linear: first operand.
        :param shaped: second operand.
        :param context: operation context.
        """
        self.context, self.linear, self.shaped = context, linear, shaped
        self._events_queue = EventsQueue(context)

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Empty, Mix, Multipoint, Multisegment]:
        """
        Computes result of the operation.
        """

    def compute_fields(self,
                       event: LeftEvent,
                       below_event: Optional[LeftEvent]) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_first
                                                is below_event.from_first)
                                            else below_event.interior_to_left)
        event.in_result = self.in_result(event)

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        events_queue.register(segments_to_endpoints(self.linear.segments),
                              True)
        for polygon in self.shaped.polygons:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon, self.context),
                    False)

    @abstractmethod
    def in_result(self, event: LeftEvent) -> bool:
        """Detects if event will be presented in result of the operation."""

    def process_event(self, event: Event, sweep_line: SweepLine) -> None:
        if not event.is_left:
            event = event.left
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

    def compute(self) -> Union_[Empty, Multisegment, Segment]:
        context = self.context
        segments_box = context.segments_box(self.linear.segments)
        if bounding.disjoint_with(segments_box,
                                  context.polygons_box(self.shaped.polygons)):
            return self.linear.value
        self.shaped.polygons = bounding.to_coupled_polygons(
                segments_box, self.shaped.polygons, context)
        if not self.shaped.polygons:
            return self.linear.value
        return unpack_segments(endpoints_to_segments([to_endpoints(event)
                                                      for event in self.sweep()
                                                      if event.in_result],
                                                     context),
                               context)

    def in_result(self, event: LeftEvent) -> bool:
        return event.from_first and event.outside

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        first_x_max = to_segments_x_max(self.linear.segments)
        while events_queue:
            event = events_queue.pop()
            if first_x_max < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.left)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Mix, Multipoint, Multisegment, Segment]:
        context = self.context
        linear_box, shaped_box = (context.segments_box(self.linear.segments),
                                  context.polygons_box(self.shaped.polygons))
        if bounding.disjoint_with(linear_box, shaped_box):
            return context.empty
        self.linear.segments = bounding.to_intersecting_segments(
                shaped_box, self.linear.segments, context)
        if not self.linear.segments:
            return context.empty
        self.shaped.polygons = bounding.to_intersecting_polygons(
                linear_box, self.shaped.polygons, context)
        if not self.shaped.polygons:
            return context.empty
        events = sorted(self.sweep(),
                        key=self._events_queue.key)
        points = []  # type: List[Point]
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not (any(event.primary.in_result for event in same_start_events)
                    or all_equal(event.from_first
                                 for event in same_start_events)):
                points.append(start)
        segments = endpoints_to_segments([to_endpoints(event)
                                          for event in events
                                          if event.is_left
                                          and event.in_result],
                                         context)
        return unpack_linear_mix(unpack_points(points, context),
                                 unpack_segments(segments, context),
                                 context)

    def in_result(self, event: LeftEvent) -> bool:
        return event.from_first and not event.outside

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_segments_x_max(self.linear.segments),
                        to_polygons_x_max(self.shaped.polygons))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Segment, Multisegment]:
        context = self.context
        linear_box, shaped_box = (context.segments_box(self.linear.segments),
                                  context.polygons_box(self.shaped.polygons))
        if bounding.disjoint_with(linear_box, shaped_box):
            return context.empty
        self.linear.segments = bounding.to_intersecting_segments(
                shaped_box, self.linear.segments, context)
        if not self.linear.segments:
            return context.empty
        self.shaped.polygons = bounding.to_intersecting_polygons(
                linear_box, self.shaped.polygons, context)
        if not self.shaped.polygons:
            return context.empty
        segments = endpoints_to_segments([to_endpoints(event)
                                          for event in self.sweep()
                                          if event.in_result], context)
        return unpack_segments(segments, context)

    def in_result(self, event: LeftEvent) -> bool:
        return event.from_first and not event.outside

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_segments_x_max(self.linear.segments),
                        to_polygons_x_max(self.shaped.polygons))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            if event.is_left:
                result.append(event)
        return result


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Mix, Multipolygon, Multisegment,
                                Polygon, Segment]:
        context = self.context
        linear_box, shaped_box = (context.segments_box(self.linear.segments),
                                  context.polygons_box(self.shaped.polygons))
        if bounding.disjoint_with(linear_box, shaped_box):
            return context.mix_cls(context.empty, self.linear.value,
                                   self.shaped.value)
        result_segments, self.linear.segments = (
            bounding.split_intersecting_segments(
                    shaped_box, self.linear.segments, context))
        self.shaped.polygons = bounding.to_intersecting_polygons(
                linear_box, self.shaped.polygons, context)
        segments = endpoints_to_segments([to_endpoints(event)
                                          for event in self.sweep()
                                          if event.in_result], context)
        segments.extend(result_segments)
        linear = unpack_segments(segments, context)
        return (self.shaped.value
                if linear is context.empty
                else context.mix_cls(context.empty, linear, self.shaped.value))

    def in_result(self, event: LeftEvent) -> bool:
        return event.from_first and event.outside

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        while events_queue:
            event = events_queue.pop()
            self.process_event(event, sweep_line)
            if event.is_left:
                result.append(event)
        return result


SymmetricDifference = Union
