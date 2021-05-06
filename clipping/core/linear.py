from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Sequence,
                    Tuple,
                    Union as Union_)

from ground.base import Context
from ground.hints import (Multisegment,
                          Point,
                          Segment)
from reprit.base import generate_repr

from . import bounding
from .event import (LeftBinaryEvent as LeftEvent,
                    RightBinaryEvent as RightEvent,
                    event_to_segment_endpoints)
from .events_queue import (LinearEventsQueue as BinaryEventsQueue,
                           NaryEventsQueue)
from .hints import (LinearMix,
                    SegmentEndpoints)
from .sweep_line import (BinarySweepLine,
                         NarySweepLine)
from .utils import (all_equal,
                    endpoints_to_segments,
                    segments_to_endpoints,
                    to_segments_x_max)

Event = Union_[LeftEvent, RightEvent]


def merge_segments(segments: Sequence[Segment],
                   context: Context) -> Multisegment:
    return context.multisegment_cls(_merge_segments(segments, context))


def _merge_segments(segments: Sequence[Segment],
                    context: Context) -> Sequence[Segment]:
    if not segments:
        return []
    events_queue = NaryEventsQueue(context)
    events_queue.register(segments_to_endpoints(segments))
    sweep_line = NarySweepLine(context)
    segments_endpoints = []  # type: List[SegmentEndpoints]
    while events_queue:
        event = events_queue.pop()
        if event.is_left:
            if event not in sweep_line:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                if above_event is not None:
                    events_queue.detect_intersection(event, above_event)
                if below_event is not None:
                    events_queue.detect_intersection(below_event, event)
        else:
            event = event.opposite
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    events_queue.detect_intersection(below_event, above_event)
                segments_endpoints.append(event_to_segment_endpoints(event))
    return endpoints_to_segments(
            sorted(endpoints for endpoints, _ in groupby(segments_endpoints)),
            context)


class Operation(ABC):
    __slots__ = 'context', 'first', 'second', '_events_queue'

    def __init__(self,
                 first: Sequence[Segment],
                 second: Sequence[Segment],
                 context: Context) -> None:
        """
        Initializes operation.

        :param first: first operand.
        :param second: second operand.
        :param context: operation context.
        """
        self.context, self.first, self.second = context, first, second
        self._events_queue = BinaryEventsQueue(context)

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[LinearMix, Multisegment]:
        """
        Computes result of the operation.
        """

    def fill_queue(self) -> None:
        self._events_queue.register(segments_to_endpoints(self.first), True)
        self._events_queue.register(segments_to_endpoints(self.second),
                                    False)

    def normalize_operands(self) -> None:
        pass

    def process_event(self,
                      event: Event,
                      sweep_line: BinarySweepLine) -> None:
        if not event.is_left:
            event = event.opposite
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)
        else:
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            if above_event is not None:
                self._events_queue.detect_intersection(event, above_event)
            if below_event is not None:
                self._events_queue.detect_intersection(below_event, event)

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        while events_queue:
            event = events_queue.pop()
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.opposite)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        return self.context.multisegment_cls(self._compute())

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        first_x_max = to_segments_x_max(self.first)
        while events_queue:
            event = events_queue.pop()
            if first_x_max < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.opposite)
        return result

    def _compute(self) -> Sequence[Segment]:
        first_box, second_box = (self.context.segments_box(self.first),
                                 self.context.segments_box(self.second))
        if bounding.disjoint_with(first_box, second_box):
            return self.first
        self.second = bounding.to_coupled_segments(first_box, self.second,
                                                   self.context)
        if not self.second:
            return self.first
        self.normalize_operands()
        return endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events
                       in groupby(self.sweep(),
                                  key=event_to_segment_endpoints)
                       if all(event.from_first for event in events)),
                self.context)


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        return self.context.multisegment_cls(self._compute())

    def sweep(self) -> Sequence[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        min_max_x = min(to_segments_x_max(self.first),
                        to_segments_x_max(self.second))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.opposite)
        return result

    def _compute(self) -> Sequence[Segment]:
        first_box, second_box = (self.context.segments_box(self.first),
                                 self.context.segments_box(self.second))
        if bounding.disjoint_with(first_box, second_box):
            return []
        self.first = bounding.to_coupled_segments(second_box, self.first,
                                                  self.context)
        self.second = bounding.to_coupled_segments(first_box, self.second,
                                                   self.context)
        if not (self.first and self.second):
            return []
        self.normalize_operands()
        return endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events
                       in groupby(self.sweep(),
                                  key=event_to_segment_endpoints)
                       if not all_equal(event.from_first for event in events)),
                self.context)


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> LinearMix:
        points, segments = self._compute()
        return (self.context.multipoint_cls(points),
                self.context.multisegment_cls(segments))

    def sweep(self) -> Sequence[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        min_max_x = min(to_segments_x_max(self.first),
                        to_segments_x_max(self.second))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result

    def _compute(self) -> Tuple[Sequence[Point], Sequence[Segment]]:
        first_box, second_box = (self.context.segments_box(self.first),
                                 self.context.segments_box(self.second))
        if bounding.disjoint_with(first_box, second_box):
            return [], []
        self.first = bounding.to_intersecting_segments(second_box, self.first,
                                                       self.context)
        self.second = bounding.to_intersecting_segments(first_box, self.second,
                                                        self.context)
        if not (self.first and self.second):
            return [], []
        self.normalize_operands()
        points = []  # type: List[Point]
        endpoints = []  # type: List[SegmentEndpoints]
        for start, same_start_events in groupby(
                sorted(self.sweep(),
                       key=event_to_segment_endpoints),
                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not all_equal(event.from_first for event in same_start_events):
                no_segment_found = True
                for event, next_event in zip(same_start_events,
                                             same_start_events[1:]):
                    if (event.from_first is not next_event.from_first
                            and event.start == next_event.start
                            and event.end == next_event.end):
                        no_segment_found = False
                        if event.is_left:
                            endpoints.append(event_to_segment_endpoints(event))
                if no_segment_found:
                    points.append(start)
        return points, endpoints_to_segments(endpoints, self.context)


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        return self.context.multisegment_cls(self._compute())

    def _compute(self) -> Sequence[Segment]:
        if bounding.disjoint_with(self.context.segments_box(self.first),
                                  self.context.segments_box(self.second)):
            result = []
            result += self.first
            result += self.second
            result.sort(key=segment_to_endpoints)
            return result
        self.normalize_operands()
        return endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events
                       in groupby(self.sweep(),
                                  key=event_to_segment_endpoints)
                       if all_equal(event.from_first for event in events)),
                self.context)


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        return self.context.multisegment_cls(self._compute())

    def _compute(self) -> Sequence[Segment]:
        if bounding.disjoint_with(self.context.segments_box(self.first),
                                  self.context.segments_box(self.second)):
            result = []
            result += self.first
            result += self.second
            result.sort(key=segment_to_endpoints)
            return result
        self.normalize_operands()
        return endpoints_to_segments(
                sorted(endpoints
                       for endpoints, _
                       in groupby(self.sweep(),
                                  key=event_to_segment_endpoints)),
                self.context)


segment_to_endpoints = attrgetter('start', 'end')
