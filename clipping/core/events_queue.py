from functools import partial
from typing import (Callable,
                    Generic,
                    Iterable,
                    Type,
                    cast)

from prioq.base import PriorityQueue
from reprit.base import generate_repr

from clipping.hints import (Point,
                            Segment)
from .enums import OverlapKind
from .event import (BinaryEvent,
                    Event,
                    HoleyEvent,
                    MixedEvent,
                    NaryEvent,
                    ShapedEvent)
from .utils import (Orientation,
                    SegmentsRelation,
                    orientation,
                    segments_intersection,
                    segments_relation)


class BinaryEventsQueueKey:
    __slots__ = 'event',

    def __init__(self, event: BinaryEvent) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'BinaryEventsQueueKey') -> bool:
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
        elif event.is_right_endpoint is not other_event.is_right_endpoint:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return event.is_right_endpoint
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            other_end_orientation = orientation(event.end, event.start,
                                                other_event.end)
            # the lowest segment is processed first
            return (other_event.from_left
                    if other_end_orientation is Orientation.COLLINEAR
                    else (other_end_orientation
                          # the lowest segment is processed first
                          is (Orientation.CLOCKWISE
                              if event.is_right_endpoint
                              else Orientation.COUNTERCLOCKWISE)))


class NaryEventsQueueKey:
    __slots__ = 'event',

    def __init__(self, event: NaryEvent) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'NaryEventsQueueKey') -> bool:
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
        elif event.is_right_endpoint is not other_event.is_right_endpoint:
            # same start, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return event.is_right_endpoint
        # same start, both events are left endpoints
        # or both are right endpoints
        else:
            # the lowest segment is processed first
            return (orientation(event.start, other_event.end, event.end)
                    is (Orientation.CLOCKWISE
                        if event.is_right_endpoint
                        else Orientation.COUNTERCLOCKWISE))


class LinearBinaryEventsQueue:
    __slots__ = '_queue',

    def __init__(self) -> None:
        self._queue = PriorityQueue(key=BinaryEventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[BinaryEvent], BinaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self,
                            below_event: BinaryEvent,
                            event: BinaryEvent) -> None:
        below_segment, segment = below_event.segment, event.segment
        relation = segments_relation(below_segment, segment)
        if (relation is SegmentsRelation.CROSS
                or relation is SegmentsRelation.TOUCH):
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = segments_intersection(below_segment, segment)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not SegmentsRelation.DISJOINT:
            # segments overlap
            if below_event.from_left is event.from_left:
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
            elif self.key(event.complement) < self.key(below_event.complement):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.complement, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

    def pop(self) -> BinaryEvent:
        return self._queue.pop()

    def register_segments(self,
                          segments: Iterable[Segment],
                          from_left: bool) -> None:
        events_queue = self._queue
        for start, end in segments:
            if start > end:
                start, end = end, start
            start_event = BinaryEvent(False, start, None, from_left)
            end_event = BinaryEvent(True, end, start_event, from_left)
            start_event.complement = end_event
            events_queue.push(start_event)
            events_queue.push(end_event)

    def _divide_segment(self, event: BinaryEvent, point: Point) -> None:
        left_event = BinaryEvent(False, point, event.complement,
                                 event.from_left)
        right_event = BinaryEvent(True, point, event, event.from_left)
        event.complement.complement, event.complement = left_event, right_event
        self._queue.push(left_event)
        self._queue.push(right_event)


class MixedBinaryEventsQueue:
    __slots__ = '_queue'

    def __init__(self) -> None:
        self._queue = PriorityQueue(key=BinaryEventsQueueKey)

    @property
    def key(self) -> Callable[[MixedEvent], BinaryEventsQueueKey]:
        return self._queue.key

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self,
                            below_event: MixedEvent,
                            event: MixedEvent) -> bool:
        below_segment, segment = below_event.segment, event.segment
        relation = segments_relation(below_segment, segment)
        if (relation is SegmentsRelation.CROSS
                or relation is SegmentsRelation.TOUCH):
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = segments_intersection(below_segment, segment)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not SegmentsRelation.DISJOINT:
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
            elif self.key(event) < self.key(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif self.key(event.complement) < self.key(below_event.complement):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.complement, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
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

    def register_segments(self,
                          segments: Iterable[Segment],
                          from_left: bool) -> None:
        queue = self._queue
        for start, end in segments:
            interior_to_left = True
            if start > end:
                start, end = end, start
                interior_to_left = False
            start_event = MixedEvent(False, start, None, from_left,
                                     interior_to_left)
            end_event = MixedEvent(True, end, start_event, from_left,
                                   interior_to_left)
            start_event.complement = end_event
            queue.push(start_event)
            queue.push(end_event)

    def _divide_segment(self, event: MixedEvent, point: Point) -> None:
        left_event = MixedEvent(False, point, event.complement,
                                event.from_left, event.interior_to_left)
        right_event = MixedEvent(True, point, event, event.from_left,
                                 event.interior_to_left)
        event.complement.complement, event.complement = left_event, right_event
        self._queue.push(left_event)
        self._queue.push(right_event)


class NaryEventsQueue:
    __slots__ = '_queue',

    def __init__(self) -> None:
        self._queue = PriorityQueue(key=NaryEventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[NaryEvent], NaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self,
                            below_event: NaryEvent,
                            event: NaryEvent) -> None:
        below_segment, segment = below_event.segment, event.segment
        relation = segments_relation(below_segment, segment)
        if (relation is SegmentsRelation.CROSS
                or relation is SegmentsRelation.TOUCH):
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = segments_intersection(below_segment, segment)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not SegmentsRelation.DISJOINT:
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
            elif self.key(event.complement) < self.key(below_event.complement):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            if starts_equal:
                # both line segments are equal or share the left endpoint
                if not ends_equal:
                    self._divide_segment(end_max.complement, end_min.start)
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

    def pop(self) -> NaryEvent:
        return self._queue.pop()

    def register_segments(self, segments: Iterable[Segment]) -> None:
        queue = self._queue
        for start, end in segments:
            if start > end:
                start, end = end, start
            start_event = NaryEvent(False, start, None)
            end_event = NaryEvent(True, end, start_event)
            start_event.complement = end_event
            queue.push(start_event)
            queue.push(end_event)

    def _divide_segment(self, event: NaryEvent, point: Point) -> None:
        left_event = NaryEvent(False, point, event.complement)
        right_event = NaryEvent(True, point, event)
        event.complement.complement, event.complement = left_event, right_event
        self._queue.push(left_event)
        self._queue.push(right_event)


class ShapedBinaryEventsQueue(Generic[Event]):
    __slots__ = 'event_cls', '_queue'

    def __init__(self, event_cls: Type[Event]) -> None:
        self.event_cls = event_cls
        self._queue = PriorityQueue(key=BinaryEventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def key(self) -> Callable[[Event], BinaryEventsQueueKey]:
        return self._queue.key

    def detect_intersection(self, below_event: Event, event: Event) -> bool:
        below_segment, segment = below_event.segment, event.segment
        relation = segments_relation(below_segment, segment)
        if (relation is SegmentsRelation.CROSS
                or relation is SegmentsRelation.TOUCH):
            if (event.start != below_event.start
                    and event.end != below_event.end):
                # segments do not intersect_multipolygons at endpoints
                point = segments_intersection(below_segment, segment)
                if point != below_event.start and point != below_event.end:
                    self._divide_segment(below_event, point)
                if point != event.start and point != event.end:
                    self._divide_segment(event, point)
        elif relation is not SegmentsRelation.DISJOINT:
            # segments overlap
            if below_event.from_left is event.from_left:
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
            elif self.key(event.complement) < self.key(below_event.complement):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            if starts_equal:
                # both line segments are equal or share the left endpoint
                below_event.overlap_kind = event.overlap_kind = (
                    OverlapKind.SAME_ORIENTATION
                    if event.interior_to_left is below_event.interior_to_left
                    else OverlapKind.DIFFERENT_ORIENTATION)
                if not ends_equal:
                    self._divide_segment(end_max.complement, end_min.start)
                return True
            elif ends_equal:
                # the line segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)
        return False

    def pop(self) -> Event:
        return self._queue.pop()

    def register_segments(self,
                          segments: Iterable[Segment],
                          from_left: bool) -> None:
        event_cls = self.event_cls
        queue = self._queue
        for start, end in segments:
            inside_on_left = True
            if start > end:
                start, end = end, start
                inside_on_left = False
            start_event = event_cls(False, start, None, from_left,
                                    inside_on_left)
            end_event = event_cls(True, end, start_event, from_left,
                                  inside_on_left)
            start_event.complement = end_event
            queue.push(start_event)
            queue.push(end_event)

    def _divide_segment(self, event: Event, point: Point) -> None:
        left_event = self.event_cls(False, point, event.complement,
                                    event.from_left, event.interior_to_left)
        right_event = self.event_cls(True, point, event, event.from_left,
                                     event.interior_to_left)
        event.complement.complement, event.complement = left_event, right_event
        self._queue.push(left_event)
        self._queue.push(right_event)


HolelessEventsQueue = cast(Callable[[], ShapedBinaryEventsQueue[ShapedEvent]],
                           partial(ShapedBinaryEventsQueue, ShapedEvent))
HoleyEventsQueue = cast(Callable[[], ShapedBinaryEventsQueue[HoleyEvent]],
                        partial(ShapedBinaryEventsQueue, HoleyEvent))
