from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Union)

from ground.base import Context
from ground.hints import (Empty,
                          Linear,
                          Maybe,
                          Mix,
                          Multipoint,
                          Point,
                          Shaped)
from reprit.base import generate_repr

from . import bounding
from .event import (LeftHolelessEvent as LeftEvent,
                    RightShapedEvent as RightEvent,
                    events_to_connectivity)
from .events_queue import HolelessEventsQueue as EventsQueue
from .hints import (Region,
                    SegmentEndpoints)
from .operands import HolelessOperand
from .sweep_line import BinarySweepLine as SweepLine
from .unpacking import (unpack_mix,
                        unpack_points,
                        unpack_regions,
                        unpack_segments)
from .utils import (all_equal,
                    contour_to_oriented_edges_endpoints,
                    endpoints_to_segments,
                    pairwise,
                    to_endpoints,
                    to_regions_x_max)

Event = Union[LeftEvent, RightEvent]


class Operation(ABC):
    __slots__ = 'context', 'first', 'second', '_events_queue'

    def __init__(self,
                 first: HolelessOperand,
                 second: HolelessOperand,
                 context: Context) -> None:
        """
        Initializes operation.

        :param first: first operand.
        :param second: second operand.
        :param context: operation context.
        """
        self.context, self.first, self.second = context, first, second
        self._events_queue = EventsQueue(context)

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union[Empty, Linear, Mix, Multipoint, Shaped]:
        """
        Computes result of the operation.
        """

    def compute_fields(self, event: LeftEvent, below_event: Optional[LeftEvent]
                       ) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_first
                                                is below_event.from_first)
                                            else below_event.interior_to_left)
        event.in_result = self.in_result(event)

    def events_to_regions(self, events: Iterable[Event]) -> Sequence[Region]:
        events = sorted([event for event in events if event.primary.in_result],
                        key=self._events_queue.key)
        for index, event in enumerate(events):
            event.position = index
        processed = [False] * len(events)
        result = []
        connectivity = events_to_connectivity(events)
        contour_cls = self.context.contour_cls
        for index, event in enumerate(events):
            if processed[index]:
                continue
            contour_start = event.start
            vertices = [contour_start]
            contour_events = [event]
            cursor = event
            opposite_position = event.opposite.position
            processed[index] = processed[opposite_position] = True
            while cursor.end != contour_start:
                vertices.append(cursor.end)
                position = _to_next_position(opposite_position, processed,
                                             connectivity)
                if position is None:
                    break
                cursor = events[position]
                contour_events.append(cursor)
                opposite_position = cursor.opposite.position
                processed[position] = processed[opposite_position] = True
            result.append(contour_cls(vertices))
        return result

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        for region in self.first.regions:
            events_queue.register(
                    contour_to_oriented_edges_endpoints(region, self.context),
                    True)
        for region in self.second.regions:
            events_queue.register(
                    contour_to_oriented_edges_endpoints(region, self.context),
                    False)

    @abstractmethod
    def in_result(self, event: LeftEvent) -> bool:
        """Detects if event will be presented in result of the operation."""

    def process_event(self,
                      event: Event,
                      processed_events: List[Event],
                      sweep_line: SweepLine) -> None:
        if not event.is_left:
            processed_events.append(event)
            event = event.left
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)
        elif event not in sweep_line:
            processed_events.append(event)
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


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Union[Empty, Linear, Mix, Multipoint, Shaped]:
        context = self.context
        first_box, second_box = (context.contours_box(self.first.regions),
                                 context.contours_box(self.second.regions))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.regions = bounding.to_intersecting_regions(
                second_box, self.first.regions, context)
        if not self.first.regions:
            return context.empty
        self.second.regions = bounding.to_intersecting_regions(
                first_box, self.second.regions, context)
        if not self.second.regions:
            return context.empty
        events = sorted(self.sweep(),
                        key=self._events_queue.key)
        points = []  # type: List[Point]
        endpoints = []  # type: List[SegmentEndpoints]
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not (any(event.is_left and event.in_result
                        for event in same_start_events)
                    or all_equal(event.from_first
                                 for event in same_start_events)):
                no_segment_found = True
                for event, next_event in pairwise(same_start_events):
                    if (event.from_first is not next_event.from_first
                            and event.start == next_event.start
                            and event.end == next_event.end):
                        no_segment_found = False
                        if event.is_left:
                            endpoints.append(to_endpoints(next_event))
                if no_segment_found and all(not event.primary.in_result
                                            for event in same_start_events):
                    points.append(start)
        segments = endpoints_to_segments(endpoints, context)
        regions = self.events_to_regions(events)
        return unpack_mix(unpack_points(points, context),
                          unpack_segments(segments, context),
                          unpack_regions(regions, context),
                          context)

    def in_result(self, event: LeftEvent) -> bool:
        return (event.inside
                or not event.from_first and event.is_common_region_boundary)

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_regions_x_max(self.first.regions),
                        to_regions_x_max(self.second.regions))
        while self._events_queue:
            event = self._events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, result, sweep_line)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Maybe[Shaped]:
        context = self.context
        first_box, second_box = (context.contours_box(self.first.regions),
                                 context.contours_box(self.second.regions))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.regions = bounding.to_coupled_regions(
                second_box, self.first.regions, context)
        if not self.first.regions:
            return context.empty
        self.second.regions = bounding.to_coupled_regions(
                first_box, self.second.regions, context)
        return (unpack_regions(self.events_to_regions(self.sweep()), context)
                if self.second.regions
                else context.empty)

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue, sweep_line = self._events_queue, SweepLine(self.context)
        min_max_x = min(to_regions_x_max(self.first.regions),
                        to_regions_x_max(self.second.regions))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: LeftEvent) -> bool:
        return (event.inside
                or not event.from_first and event.is_common_region_boundary)


def _to_next_position(position: int,
                      processed: List[bool],
                      connectivity: Sequence[int]) -> Optional[int]:
    candidate = position
    while True:
        candidate = connectivity[candidate]
        if not processed[candidate]:
            return candidate
        elif candidate == position:
            return None
