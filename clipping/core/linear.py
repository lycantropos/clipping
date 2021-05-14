from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Sequence,
                    Union as Union_)

from ground.base import (Context,
                         Orientation,
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
from .hints import SegmentEndpoints
from .operands import LinearOperand
from .sweep_line import (BinarySweepLine,
                         NarySweepLine)
from .unpacking import (unpack_linear_mix,
                        unpack_points,
                        unpack_segments)
from .utils import (all_equal,
                    endpoints_to_segments,
                    flatten,
                    segments_to_endpoints,
                    to_endpoints,
                    to_ordered_set,
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
    __slots__ = 'context', 'first', 'second', '_events_queue'

    def __init__(self,
                 first: LinearOperand,
                 second: LinearOperand,
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
    def compute(self) -> Union_[Empty, Mix, Multipoint, Multisegment, Segment]:
        """
        Computes result of the operation.
        """

    def fill_queue(self) -> None:
        self._events_queue.register(
                segments_to_endpoints(self.first.segments), True)
        self._events_queue.register(
                segments_to_endpoints(self.second.segments), False)

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
            return self.first.value
        self.second.segments = bounding.to_coupled_segments(
                first_box, self.second.segments, context)
        if not self.second.segments:
            return self.first.value
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
        first_x_max = to_segments_x_max(self.first.segments)
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
        first_box, second_box = (context.segments_box(self.first.segments),
                                 context.segments_box(self.second.segments))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.segments = bounding.to_coupled_segments(
                second_box, self.first.segments, context)
        if not self.first.segments:
            return context.empty
        self.second.segments = bounding.to_coupled_segments(
                first_box, self.second.segments, context)
        if not self.second.segments:
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
        min_max_x = min(to_segments_x_max(self.first.segments),
                        to_segments_x_max(self.second.segments))
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
        first_box, second_box = (context.segments_box(self.first.segments),
                                 context.segments_box(self.second.segments))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.segments = bounding.to_intersecting_segments(
                second_box, self.first.segments, context)
        if not self.first.segments:
            return context.empty
        self.second.segments = bounding.to_intersecting_segments(
                first_box, self.second.segments, context)
        if not self.second.segments:
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
        min_max_x = min(to_segments_x_max(self.first.segments),
                        to_segments_x_max(self.second.segments))
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
        if bounding.disjoint_with(context.segments_box(self.first.segments),
                                  context.segments_box(self.second.segments)):
            segments = []
            segments += self.first.segments
            segments += self.second.segments
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
        if bounding.disjoint_with(context.segments_box(self.first.segments),
                                  context.segments_box(self.second.segments)):
            segments = []
            segments += self.first.segments
            segments += self.second.segments
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
        return (first
                if relation is Relation.EQUAL or relation is Relation.COMPONENT
                else
                (second
                 if relation is Relation.COMPOSITE
                 else _intersect_segments_overlap(first, second, context)))


def subtract_segments(minuend: Segment,
                      subtrahend: Segment,
                      context: Context
                      ) -> Union_[Empty, Multisegment, Segment]:
    relation = context.segments_relation(minuend, subtrahend)
    if relation is Relation.COMPONENT or relation is Relation.EQUAL:
        return context.empty
    elif (relation is Relation.DISJOINT
          or relation is Relation.TOUCH
          or relation is Relation.CROSS):
        return minuend
    else:
        return (_subtract_segments_overlap(minuend, subtrahend, context)
                if relation is Relation.OVERLAP
                else _subtract_segments_composite(minuend, subtrahend,
                                                  context))


def symmetric_subtract_segments(first: Segment,
                                second: Segment,
                                context: Context
                                ) -> Union_[Empty, Multisegment, Segment]:
    relation = context.segments_relation(first, second)
    if relation is Relation.DISJOINT:
        return context.multisegment_cls([first, second])
    elif relation is Relation.EQUAL:
        return context.empty
    else:
        return (_unite_segments_touch(first, second, context)
                if relation is Relation.TOUCH
                else
                (_unite_segments_cross(first, second, context)
                 if relation is Relation.CROSS
                 else
                 (_symmetric_subtract_segments_overlap(first, second, context)
                  if relation is Relation.OVERLAP
                  else (_subtract_segments_composite(first, second, context)
                        if relation is Relation.COMPOSITE
                        else _subtract_segments_composite(second, first,
                                                          context)))))


def unite_segments(first: Segment,
                   second: Segment,
                   context: Context) -> Union_[Multisegment, Segment]:
    relation = context.segments_relation(first, second)
    if relation is Relation.DISJOINT:
        return context.multisegment_cls([first, second])
    elif relation is Relation.EQUAL or relation is Relation.COMPOSITE:
        return first
    elif relation is Relation.COMPONENT:
        return second
    else:
        return (_unite_segments_touch
                if relation is Relation.TOUCH
                else (_unite_segments_cross
                      if relation is Relation.CROSS
                      else _unite_segments_overlap))(first, second, context)


def complete_intersect_segment_with_multisegment(
        segment: Segment,
        multisegment: Multisegment,
        context: Context
) -> Union_[Empty, Mix, Multipoint, Multisegment, Segment]:
    points, segments = [], []
    to_intersection_point = context.segments_intersection
    for sub_segment in multisegment.segments:
        relation = context.segments_relation(segment, sub_segment)
        if relation is Relation.TOUCH or relation is Relation.CROSS:
            points.append(to_intersection_point(segment, sub_segment))
        elif relation is not Relation.DISJOINT:
            segments.append(segment
                            if (relation is Relation.EQUAL
                                or relation is Relation.COMPONENT)
                            else (sub_segment
                                  if relation is Relation.COMPOSITE
                                  else _intersect_segments_overlap(segment,
                                                                   sub_segment,
                                                                   context)))
    points = list(to_ordered_set(points)
                  - set(flatten(to_endpoints(segment)
                                for segment in segments)))
    return unpack_linear_mix(unpack_points(points, context),
                             unpack_segments(segments, context),
                             context)


def intersect_segment_with_multisegment(segment: Segment,
                                        multisegment: Multisegment,
                                        context: Context
                                        ) -> Union_[Empty, Multisegment,
                                                    Segment]:
    segments = _intersect_segment_with_multisegment(segment, multisegment,
                                                    context)
    return unpack_segments(segments, context)


def subtract_segment_from_multisegment(multisegment: Multisegment,
                                       segment: Segment,
                                       context: Context
                                       ) -> Union_[Empty, Multisegment,
                                                   Segment]:
    segments = _subtract_segment_from_multisegment(multisegment, segment,
                                                   context)
    return unpack_segments(segments, context)


def unite_segment_with_multisegment(segment: Segment,
                                    multisegment: Multisegment,
                                    context: Context
                                    ) -> Union_[Multisegment, Segment]:
    segments = _subtract_segment_from_multisegment(multisegment, segment,
                                                   context)
    segments.append(segment)
    return unpack_segments(segments, context)


def _intersect_segment_with_multisegment(segment: Segment,
                                         multisegment: Multisegment,
                                         context: Context) -> List[Segment]:
    result = []
    for sub_segment in multisegment.segments:
        relation = context.segments_relation(segment, sub_segment)
        if (relation is not Relation.DISJOINT
                and relation is not Relation.TOUCH
                and relation is not Relation.CROSS):
            result.append(segment
                          if (relation is Relation.EQUAL
                              or relation is Relation.COMPONENT)
                          else (sub_segment
                                if relation is Relation.COMPOSITE
                                else _intersect_segments_overlap(segment,
                                                                 sub_segment,
                                                                 context)))
    return result


def _subtract_segment_from_multisegment(multisegment: Multisegment,
                                        segment: Segment,
                                        context: Context
                                        ) -> List[Segment]:
    result = []
    for index, sub_segment in enumerate(multisegment.segments):
        relation = context.segments_relation(segment, sub_segment)
        if relation is Relation.EQUAL:
            result.extend(multisegment.segments[index + 1:])
            break
        elif relation is Relation.COMPONENT:
            left_start, left_end, right_start, right_end = sorted([
                sub_segment.start, sub_segment.end, segment.start,
                segment.end])
            result.extend(
                    [context.segment_cls(right_start, right_end)]
                    if left_start == segment.start or left_start == segment.end
                    else
                    ((([context.segment_cls(left_start, left_end)]
                       if right_start == right_end
                       else [context.segment_cls(left_start, left_end),
                             context.segment_cls(right_start, right_end)])
                      if (right_start == segment.start
                          or right_start == segment.end)
                      else [context.segment_cls(left_start, left_end)])
                     if left_end == segment.start or left_end == segment.end
                     else [context.segment_cls(left_start, right_start)]))
            result.extend(multisegment.segments[index + 1:])
            break
        elif relation is Relation.OVERLAP:
            result.append(_subtract_segments_overlap(sub_segment, segment,
                                                     context))
        elif relation is not Relation.COMPOSITE:
            result.append(sub_segment)
    return result


def _subtract_segments_composite(minuend: Segment,
                                 subtrahend: Segment,
                                 context: Context
                                 ) -> Union_[Multisegment, Segment]:
    left_start, left_end, right_start, right_end = sorted([
        minuend.start, minuend.end, subtrahend.start, subtrahend.end])
    return (context.segment_cls(right_start, right_end)
            if left_start == subtrahend.start or left_start == subtrahend.end
            else (((context.segment_cls(left_start, left_end)
                    if right_start == right_end
                    else
                    context.multisegment_cls([context.segment_cls(left_start,
                                                                  left_end),
                                              context.segment_cls(right_start,
                                                                  right_end)]))
                   if (right_start == subtrahend.start
                       or right_start == subtrahend.end)
                   else context.segment_cls(left_start, left_end))
                  if left_end == subtrahend.start or left_end == subtrahend.end
                  else context.segment_cls(left_start, right_start)))


def _subtract_segments_overlap(minuend: Segment,
                               subtrahend: Segment,
                               context: Context) -> Segment:
    left_start, left_end, right_start, right_end = sorted([
        minuend.start, minuend.end, subtrahend.start, subtrahend.end])
    return (context.segment_cls(left_start, left_end)
            if left_start == minuend.start or left_start == minuend.end
            else context.segment_cls(right_start, right_end))


def _symmetric_subtract_segments_overlap(minuend: Segment,
                                         subtrahend: Segment,
                                         context: Context) -> Multisegment:
    left_start, left_end, right_start, right_end = sorted([
        minuend.start, minuend.end, subtrahend.start, subtrahend.end])
    return context.multisegment_cls([context.segment_cls(left_start, left_end),
                                     context.segment_cls(right_start,
                                                         right_end)])


def _unite_segments_cross(first: Segment,
                          second: Segment,
                          context: Context) -> Multisegment:
    cross_point = context.segments_intersection(first, second)
    segment_cls = context.segment_cls
    return context.multisegment_cls([segment_cls(first.start, cross_point),
                                     segment_cls(second.start, cross_point),
                                     segment_cls(cross_point, first.end),
                                     segment_cls(cross_point, second.end)])


def _unite_segments_overlap(first: Segment,
                            second: Segment,
                            context: Context) -> Segment:
    start, _, _, end = sorted([first.start, first.end, second.start,
                               second.end])
    return context.segment_cls(start, end)


def _unite_segments_touch(first: Segment,
                          second: Segment,
                          context: Context) -> Union_[Multisegment, Segment]:
    return (context.multisegment_cls([first, second])
            if ((first.start != second.start
                 or (context.angle_orientation(first.start, first.end,
                                               second.end)
                     is not Orientation.COLLINEAR))
                and (first.start != second.end
                     or (context.angle_orientation(first.start, first.end,
                                                   second.start)
                         is not Orientation.COLLINEAR))
                and (first.end != second.start
                     or (context.angle_orientation(first.end, first.start,
                                                   second.end)
                         is not Orientation.COLLINEAR))
                and (first.end != second.end
                     or (context.angle_orientation(first.end, first.start,
                                                   second.start)
                         is not Orientation.COLLINEAR)))
            else context.segment_cls(min(first.start, first.end,
                                         second.start, second.end),
                                     max(first.start, first.end,
                                         second.start, second.end)))


def _intersect_segments_overlap(first: Segment,
                                second: Segment,
                                context: Context) -> Segment:
    _, start, end, _ = sorted([first.start, first.end, second.start,
                               second.end])
    return context.segment_cls(start, end)
