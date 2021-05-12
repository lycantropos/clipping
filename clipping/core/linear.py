from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Sequence,
                    Union as Union_)

from ground.base import (Context,
                         Relation)
from ground.hints import (Empty,
                          Mix,
                          Multipoint,
                          Multisegment,
                          Point,
                          Segment)
from reprit.base import generate_repr

from . import bounding
from .event import (LeftBinaryEvent as LeftEvent,
                    RightBinaryEvent as RightEvent)
from .events_queue import (LinearEventsQueue as BinaryEventsQueue,
                           NaryEventsQueue)
from .hints import (SegmentEndpoints)
from .sweep_line import (BinarySweepLine,
                         NarySweepLine)
from .unpacking import (unpack_linear_mix,
                        unpack_points,
                        unpack_segments)
from .utils import (all_equal,
                    endpoints_to_segments,
                    segments_to_endpoints,
                    to_endpoints,
                    to_segments_x_max)

Event = Union_[LeftEvent, RightEvent]


def merge_segments(segments: Sequence[Segment],
                   context: Context) -> Union_[Empty, Segment, Multisegment]:
    return unpack_segments(_merge_segments(segments, context), context)


def _merge_segments(segments: Sequence[Segment],
                    context: Context) -> Sequence[Segment]:
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
            event = event.left
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    events_queue.detect_intersection(below_event, above_event)
                segments_endpoints.append(to_endpoints(event))
    return endpoints_to_segments(
            sorted(endpoints for endpoints, _ in groupby(segments_endpoints)),
            context)


class Operation(ABC):
    __slots__ = ('context', 'first', 'second', '_events_queue',
                 '_first_segments', '_second_segments')

    def __init__(self,
                 first: Multisegment,
                 second: Multisegment,
                 context: Context) -> None:
        """
        Initializes operation.

        :param first: first operand.
        :param second: second operand.
        :param context: operation context.
        """
        self.context, self.first, self.second = context, first, second
        self._first_segments, self._second_segments = (first.segments,
                                                       second.segments)
        self._events_queue = BinaryEventsQueue(context)

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Empty, Mix, Multipoint, Multisegment, Segment]:
        """
        Computes result of the operation.
        """

    def fill_queue(self) -> None:
        self._events_queue.register(
                segments_to_endpoints(self._first_segments), True)
        self._events_queue.register(
                segments_to_endpoints(self._second_segments), False)

    def process_event(self,
                      event: Event,
                      sweep_line: BinarySweepLine) -> None:
        if event.is_left:
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            if above_event is not None:
                self._events_queue.detect_intersection(event, above_event)
            if below_event is not None:
                self._events_queue.detect_intersection(below_event, event)
        else:
            event = event.left
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        while events_queue:
            event = events_queue.pop()
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.left)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Segment, Multisegment]:
        context = self.context
        first_box, second_box = (
            context.segments_box(self.first.segments),
            context.segments_box(self.second.segments))
        if bounding.disjoint_with(first_box, second_box):
            return self.first
        self._second_segments = bounding.to_coupled_segments(
                first_box, self._second_segments, context)
        if not self._second_segments:
            return self.first
        return unpack_segments(endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events in groupby(self.sweep(),
                                                        key=to_endpoints)
                       if all(event.from_first for event in events)),
                context),
                context)

    def sweep(self) -> Iterable[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        first_x_max = to_segments_x_max(self._first_segments)
        while events_queue:
            event = events_queue.pop()
            if first_x_max < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.left)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Segment, Multisegment]:
        context = self.context
        first_box, second_box = (context.segments_box(self._first_segments),
                                 context.segments_box(self._second_segments))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self._first_segments = bounding.to_coupled_segments(
                second_box, self._first_segments, context)
        if not self._first_segments:
            return context.empty
        self._second_segments = bounding.to_coupled_segments(
                first_box, self._second_segments, context)
        if not self._second_segments:
            return context.empty
        return unpack_segments(endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events in groupby(self.sweep(),
                                                        key=to_endpoints)
                       if not all_equal(event.from_first for event in events)),
                context),
                context)

    def sweep(self) -> Sequence[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        min_max_x = min(to_segments_x_max(self._first_segments),
                        to_segments_x_max(self._second_segments))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            if not event.is_left:
                result.append(event.left)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Mix, Multipoint, Multisegment, Segment]:
        context = self.context
        first_box, second_box = (context.segments_box(self._first_segments),
                                 context.segments_box(self._second_segments))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self._first_segments = bounding.to_intersecting_segments(
                second_box, self._first_segments, context)
        if not self._first_segments:
            return context.empty
        self._second_segments = bounding.to_intersecting_segments(
                first_box, self._second_segments, context)
        if not self._second_segments:
            return context.empty
        points = []  # type: List[Point]
        endpoints = []  # type: List[SegmentEndpoints]
        for start, same_start_events in groupby(sorted(self.sweep(),
                                                       key=to_endpoints),
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
                            endpoints.append(to_endpoints(event))
                if no_segment_found:
                    points.append(start)
        segments = endpoints_to_segments(endpoints, context)
        return unpack_linear_mix(unpack_points(points, context),
                                 unpack_segments(segments, context),
                                 context)

    def sweep(self) -> Sequence[LeftEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
        min_max_x = min(to_segments_x_max(self._first_segments),
                        to_segments_x_max(self._second_segments))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Segment, Multisegment]:
        context = self.context
        if bounding.disjoint_with(context.segments_box(self._first_segments),
                                  context.segments_box(self._second_segments)):
            segments = []
            segments += self._first_segments
            segments += self._second_segments
            segments.sort(key=to_endpoints)
            return context.multisegment_cls(segments)
        return unpack_segments(endpoints_to_segments(
                sorted(endpoints
                       for endpoints, events in groupby(self.sweep(),
                                                        key=to_endpoints)
                       if all_equal(event.from_first for event in events)),
                context),
                context)


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        context = self.context
        if bounding.disjoint_with(context.segments_box(self._first_segments),
                                  context.segments_box(self._second_segments)):
            segments = []
            segments += self._first_segments
            segments += self._second_segments
            segments.sort(key=to_endpoints)
            return context.multisegment_cls(segments)
        return context.multisegment_cls(endpoints_to_segments(
                sorted(endpoints
                       for endpoints, _ in groupby(self.sweep(),
                                                   key=to_endpoints)),
                context))


def intersect_segments(first: Segment,
                       second: Segment,
                       context: Context) -> Union_[Empty, Multipoint, Segment]:
    relation = context.segments_relation(first, second)
    if relation is Relation.DISJOINT:
        return context.empty
    elif relation is Relation.TOUCH or relation is Relation.CROSS:
        return context.multipoint_cls([context.segments_intersection(first,
                                                                     second)])
    else:
        _, overlap_start, overlap_end, _ = sorted([first.start, first.end,
                                                   second.start, second.end])
        return context.segment_cls(overlap_start, overlap_end)
