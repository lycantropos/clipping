from functools import partial
from typing import (Callable,
                    Generic,
                    Iterable,
                    Type,
                    Union,
                    cast)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import Point
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .enums import OverlapKind
from .event import (LeftBinaryEvent,
                    LeftHolelessEvent,
                    LeftHoleyEvent,
                    LeftMixedEvent,
                    LeftNaryEvent,
                    LeftShapedEvent,
                    RightBinaryEvent,
                    RightMixedEvent,
                    RightNaryEvent,
                    RightShapedEvent)
from .hints import (Orienteer,
                    SegmentEndpoints)

BinaryEvent = Union[LeftBinaryEvent, RightBinaryEvent]
NaryEvent = Union[LeftNaryEvent, RightNaryEvent]
MixedEvent = Union[LeftMixedEvent, RightMixedEvent]
ShapedEvent = Union[LeftShapedEvent, RightShapedEvent]


class BinaryEventsQueueKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self, orienteer: Orienteer, event: BinaryEvent) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'BinaryEventsQueueKey') -> bool:
        event, other_event = self.event, other.event
        start, other_start = event.start, other_event.start
        if start.x != other_start.x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start.x < other_start.x
        elif start.y != other_start.y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start.y < other_start.y
        elif event.is_left is not other_event.is_left:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return not event.is_left
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            other_end_orientation = self.orienteer(event.start, event.end,
                                                   other_event.end)
            # the lowest segment is processed first
            return (other_event.from_first
                    if other_end_orientation is Orientation.COLLINEAR
                    else (other_end_orientation
                          # the lowest segment is processed first
                          is (Orientation.COUNTERCLOCKWISE
                              if event.is_left
                              else Orientation.CLOCKWISE)))


class NaryEventsQueueKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self, orienteer: Orienteer, event: NaryEvent) -> None:
        self.orienteer, self.event = orienteer, event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'NaryEventsQueueKey') -> bool:
        event, other_event = self.event, other.event
        start, other_start = event.start, other_event.start
        if start.x != other_start.x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start.x < other_start.x
        elif start.y != other_start.y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start.y < other_start.y
        elif event.is_left is not other_event.is_left:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return not event.is_left
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            # the lowest segment is processed first
            return (self.orienteer(event.start, event.end, other_event.end)
                    is (Orientation.COUNTERCLOCKWISE
                        if event.is_left
                        else Orientation.CLOCKWISE))


class LinearEventsQueue:
    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=partial(BinaryEventsQueueKey,
                                                context.angle_orientation))

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[BinaryEvent], BinaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self,
                            below_event: LeftBinaryEvent,
                            event: LeftBinaryEvent) -> None:
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.CROSS or relation is Relation.TOUCH:
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = self.context.segments_intersection(below_event, event)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            if below_event.from_first is event.from_first:
                raise ValueError('Segments of the same multisegment '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            if starts_equal:
                start_min = start_max = None
            elif self.key(event) < self.key(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif self.key(event.opposite) < self.key(below_event.opposite):
                end_min, end_max = event.opposite, below_event.opposite
            else:
                end_min, end_max = below_event.opposite, event.opposite
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.opposite, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.opposite:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

    def pop(self) -> BinaryEvent:
        return self._queue.pop()

    def register(self,
                 segments_endpoints: Iterable[SegmentEndpoints],
                 from_first: bool) -> None:
        events_queue = self._queue
        for segment_endpoints in segments_endpoints:
            event = LeftBinaryEvent.from_segment_endpoints(segment_endpoints,
                                                           from_first)
            events_queue.push(event)
            events_queue.push(event.opposite)

    def _divide_segment(self, event: LeftBinaryEvent, point: Point) -> None:
        tail = event.divide(point)
        self._queue.push(tail)
        self._queue.push(event.opposite)


class MixedEventsQueue:
    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=partial(BinaryEventsQueueKey,
                                                context.angle_orientation))

    @property
    def key(self) -> Callable[[MixedEvent], BinaryEventsQueueKey]:
        return self._queue.key

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self,
                            below_event: LeftMixedEvent,
                            event: LeftMixedEvent) -> bool:
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.CROSS or relation is Relation.TOUCH:
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = self.context.segments_intersection(below_event, event)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            if below_event.from_first is event.from_first:
                raise ValueError('Edges of the {geometry} '
                                 'should not overlap.'
                                 .format(geometry=('multisegment'
                                                   if event.from_first
                                                   else 'multipolygon')))
            event.is_overlap = below_event.is_overlap = True
            starts_equal = below_event.start == event.start
            if starts_equal:
                start_min = start_max = None
            elif self.key(event) < self.key(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif self.key(event.opposite) < self.key(below_event.opposite):
                end_min, end_max = event.opposite, below_event.opposite
            else:
                end_min, end_max = below_event.opposite, event.opposite
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.opposite, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.opposite:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)
        return False

    def pop(self) -> MixedEvent:
        return self._queue.pop()

    def register(self,
                 segments_endpoints: Iterable[SegmentEndpoints],
                 from_first: bool) -> None:
        push = self._queue.push
        for segment_endpoints in segments_endpoints:
            event = LeftMixedEvent.from_endpoints(segment_endpoints,
                                                  from_first)
            push(event)
            push(event.opposite)

    def _divide_segment(self, event: LeftMixedEvent, point: Point) -> None:
        tail = event.divide(point)
        self._queue.push(tail)
        self._queue.push(event.opposite)


class NaryEventsQueue:
    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=partial(NaryEventsQueueKey,
                                                context.angle_orientation))

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[NaryEvent], NaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self,
                            below_event: LeftNaryEvent,
                            event: LeftNaryEvent) -> None:
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.CROSS or relation is Relation.TOUCH:
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = self.context.segments_intersection(below_event, event)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            starts_equal = below_event.start == event.start
            if starts_equal:
                start_min = start_max = None
            elif self.key(event) < self.key(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif self.key(event.opposite) < self.key(below_event.opposite):
                end_min, end_max = event.opposite, below_event.opposite
            else:
                end_min, end_max = below_event.opposite, event.opposite
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.opposite, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.opposite:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

    def pop(self) -> NaryEvent:
        return self._queue.pop()

    def register(self, segments_endpoints: Iterable[SegmentEndpoints]) -> None:
        push = self._queue.push
        for segment_endpoints in segments_endpoints:
            event = LeftNaryEvent.from_segment_endpoints(segment_endpoints)
            push(event)
            push(event.opposite)

    def _divide_segment(self, event: LeftNaryEvent, point: Point) -> None:
        tail = LeftNaryEvent.divide(event, point)
        self._queue.push(tail)
        self._queue.push(event.opposite)


class ShapedEventsQueue(Generic[LeftShapedEvent]):
    __slots__ = 'context', 'event_cls', '_queue'

    def __init__(self,
                 event_cls: Type[LeftShapedEvent],
                 context: Context) -> None:
        self.event_cls, self.context = event_cls, context
        self._queue = PriorityQueue(key=partial(BinaryEventsQueueKey,
                                                context.angle_orientation))

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[ShapedEvent], BinaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self,
                            below_event: LeftShapedEvent,
                            event: LeftShapedEvent) -> bool:
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.CROSS or relation is Relation.TOUCH:
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = self.context.segments_intersection(below_event, event)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not Relation.DISJOINT:
            # segments overlap
            if below_event.from_first is event.from_first:
                raise ValueError('Edges of the same multipolygon '
                                 'should not overlap.')
            starts_equal = below_event.start == event.start
            if starts_equal:
                start_min = start_max = None
            elif self.key(event) < self.key(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif self.key(event.opposite) < self.key(below_event.opposite):
                end_min, end_max = event.opposite, below_event.opposite
            else:
                end_min, end_max = below_event.opposite, event.opposite
            if starts_equal:
                # both line segments are equal or share the left endpoint
                below_event.overlap_kind = event.overlap_kind = (
                    OverlapKind.SAME_ORIENTATION
                    if event.interior_to_left is below_event.interior_to_left
                    else OverlapKind.DIFFERENT_ORIENTATION)
                if not ends_equal:
                    self._divide_segment(end_max.opposite, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.opposite:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)
        return False

    def pop(self) -> ShapedEvent:
        return self._queue.pop()

    def register(self,
                 segments_endpoints: Iterable[SegmentEndpoints],
                 from_first: bool) -> None:
        event_cls, push = self.event_cls, self._queue.push
        for segment_endpoints in segments_endpoints:
            event = event_cls.from_endpoints(segment_endpoints, from_first)
            push(event)
            push(event.opposite)

    def _divide_segment(self, event: LeftShapedEvent, point: Point) -> None:
        tail = event.divide(point)
        self._queue.push(tail)
        self._queue.push(event.opposite)


HolelessEventsQueue = cast(Callable[[Context],
                                    ShapedEventsQueue[LeftHolelessEvent]],
                           partial(ShapedEventsQueue, LeftHolelessEvent))
HoleyEventsQueue = cast(Callable[[Context],
                                 ShapedEventsQueue[LeftHoleyEvent]],
                        partial(ShapedEventsQueue, LeftHoleyEvent))
