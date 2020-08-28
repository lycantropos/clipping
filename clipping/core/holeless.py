from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (List,
                    Optional,
                    Union as Union_)

from reprit.base import generate_repr

from clipping.hints import (HolelessMix,
                            Multipoint,
                            Multiregion,
                            Multisegment)
from . import bounding_box
from .event import (ShapedEvent as Event,
                    events_to_connectivity)
from .events_queue import (BinaryEventsQueueKey as EventsQueueKey,
                           HolelessEventsQueue as EventsQueue)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    contour_to_oriented_segments,
                    pairwise,
                    to_multiregion_base,
                    to_multiregion_x_max,
                    to_rational_multiregion)


class Operation(ABC):
    __slots__ = 'left', 'right', 'accurate', '_events_queue'

    def __init__(self,
                 left: Multiregion,
                 right: Multiregion,
                 accurate: bool) -> None:
        """
        Initializes operation.

        :param left: left operand.
        :param right: right operand.
        :param accurate:
            flag that tells whether to use slow but more accurate arithmetic
            for floating point numbers.
        """
        self.left = left
        self.right = right
        self.accurate = accurate
        self._events_queue = EventsQueue()

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Multiregion, HolelessMix]:
        """
        Computes result of the operation.
        """

    def compute_fields(self, event: Event, below_event: Optional[Event]
                       ) -> None:
        if below_event is not None:
            event.other_interior_to_left = (below_event.other_interior_to_left
                                            if (event.from_left
                                                is below_event.from_left)
                                            else below_event.interior_to_left)
        event.in_result = self.in_result(event)

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        for region in self.left:
            events_queue.register_segments(
                    contour_to_oriented_segments(region), True)
        for region in self.right:
            events_queue.register_segments(
                    contour_to_oriented_segments(region), False)

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def normalize_operands(self) -> None:
        left, right = self.left, self.right
        if self.accurate and not issubclass(to_multiregion_base(left + right),
                                            Rational):
            self.left, self.right = (to_rational_multiregion(left),
                                     to_rational_multiregion(right))

    def process_event(self, event: Event, processed_events: List[Event],
                      sweep_line: SweepLine) -> None:
        if event.is_right_endpoint:
            processed_events.append(event)
            event = event.complement
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

    def compute(self) -> HolelessMix:
        if not (self.left and self.right):
            return [], [], []
        left_bounding_box = bounding_box.from_multiregion(self.left)
        right_bounding_box = bounding_box.from_multiregion(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return [], [], []
        self.left = bounding_box.to_intersecting_regions(right_bounding_box,
                                                         self.left)
        self.right = bounding_box.to_intersecting_regions(left_bounding_box,
                                                          self.right)
        if not (self.left and self.right):
            return [], [], []
        self.normalize_operands()
        events = sorted(self.sweep(),
                        key=EventsQueueKey)
        multipoint = []  # type: Multipoint
        multisegment = []  # type: Multisegment
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if (all(event.is_right_endpoint or not event.in_result
                    for event in same_start_events)
                    and not all_equal(event.from_left
                                      for event in same_start_events)):
                no_segment_found = True
                for event, next_event in pairwise(same_start_events):
                    if (event.from_left is not next_event.from_left
                            and event.segment == next_event.segment):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            multisegment.append(next_event.segment)
                if no_segment_found and all(not event.complement.in_result
                                            if event.is_right_endpoint
                                            else not event.in_result
                                            for event in same_start_events):
                    multipoint.append(start)
        return multipoint, multisegment, events_to_multiregion(events)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multiregion_x_max(self.left),
                        to_multiregion_x_max(self.right))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multiregion:
        if not (self.left and self.right):
            return []
        left_bounding_box = bounding_box.from_multiregion(self.left)
        right_bounding_box = bounding_box.from_multiregion(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return []
        self.left = bounding_box.to_coupled_regions(right_bounding_box,
                                                    self.left)
        self.right = bounding_box.to_coupled_regions(left_bounding_box,
                                                     self.right)
        if not (self.left and self.right):
            return []
        self.normalize_operands()
        return events_to_multiregion(self.sweep())

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine()
        min_max_x = min(to_multiregion_x_max(self.left),
                        to_multiregion_x_max(self.right))
        while self._events_queue:
            event = self._events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)


def events_to_multiregion(events: List[Event]) -> Multiregion:
    events = sorted([event for event in events if event.primary.in_result],
                    key=EventsQueueKey)
    for index, event in enumerate(events):
        event.position = index
    processed = [False] * len(events)
    result = []
    connectivity = events_to_connectivity(events)
    for index, event in enumerate(events):
        if processed[index]:
            continue
        contour_start = event.start
        contour = [contour_start]
        contour_events = [event]
        cursor = event
        complement_position = event.complement.position
        processed[index] = processed[complement_position] = True
        while cursor.end != contour_start:
            contour.append(cursor.end)
            position = _to_next_position(complement_position, processed,
                                         connectivity)
            if position is None:
                break
            cursor = events[position]
            contour_events.append(cursor)
            complement_position = cursor.complement.position
            processed[position] = processed[complement_position] = True
        result.append(contour)
    return result


def _to_next_position(position: int,
                      processed: List[bool],
                      connectivity: List[int]) -> Optional[int]:
    candidate = position
    while True:
        candidate = connectivity[candidate]
        if not processed[candidate]:
            return candidate
        elif candidate == position:
            return None
