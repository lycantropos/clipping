from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from numbers import Rational
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Union as Union_)

from reprit.base import generate_repr

from clipping.hints import (Mix,
                            Multipoint,
                            Multisegment,
                            Segment)
from . import bounding_box
from .event import BinaryEvent
from .events_queue import (LinearBinaryEventsQueue as BinaryEventsQueue,
                           NaryEventsQueue)
from .sweep_line import (BinarySweepLine,
                         NarySweepLine)
from .utils import (all_equal,
                    to_multisegment_base,
                    to_multisegment_x_max,
                    to_rational_multisegment)


def merge_segments(segments: List[Segment],
                   accurate: bool) -> Iterable[Segment]:
    if not segments:
        return
    if accurate and not issubclass(to_multisegment_base(segments), Rational):
        segments = to_rational_multisegment(segments)
    events_queue = NaryEventsQueue()
    events_queue.register_segments(segments)
    sweep_line = NarySweepLine()
    while events_queue:
        event = events_queue.pop()
        if event.is_right_endpoint:
            event = event.complement
            if event in sweep_line:
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                sweep_line.remove(event)
                if above_event is not None and below_event is not None:
                    events_queue.detect_intersection(below_event, above_event)
                yield event.segment
        elif event not in sweep_line:
            sweep_line.add(event)
            above_event, below_event = (sweep_line.above(event),
                                        sweep_line.below(event))
            if above_event is not None:
                events_queue.detect_intersection(event, above_event)
            if below_event is not None:
                events_queue.detect_intersection(below_event, event)


class Operation(ABC):
    __slots__ = 'left', 'right', 'accurate', '_events_queue'

    def __init__(self,
                 left: Multisegment,
                 right: Multisegment,
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
        self._events_queue = BinaryEventsQueue()

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Multisegment, Mix]:
        """
        Computes result of the operation.
        """

    def fill_queue(self) -> None:
        self._events_queue.register_segments(self.left, True)
        self._events_queue.register_segments(self.right, False)

    def normalize_operands(self) -> None:
        left, right = self.left, self.right
        if (self.accurate
                and not issubclass(to_multisegment_base(left + right),
                                   Rational)):
            self.left, self.right = (to_rational_multisegment(left),
                                     to_rational_multisegment(right))

    def process_event(self, event: BinaryEvent,
                      sweep_line: BinarySweepLine) -> None:
        if event.is_right_endpoint:
            event = event.complement
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

    def sweep(self) -> List[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine()
        while events_queue:
            event = events_queue.pop()
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return self.left
        left_bounding_box = bounding_box.from_multisegment(self.left)
        right_bounding_box = bounding_box.from_multisegment(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return self.left
        self.right = bounding_box.to_coupled_segments(left_bounding_box,
                                                      self.right)
        if not self.right:
            return self.left
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if all(event.from_left for event in events))

    def sweep(self) -> List[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine()
        left_x_max = to_multisegment_x_max(self.left)
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > left_x_max:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return []
        left_bounding_box = bounding_box.from_multisegment(self.left)
        right_bounding_box = bounding_box.from_multisegment(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return []
        self.left = bounding_box.to_coupled_segments(right_bounding_box,
                                                     self.left)
        self.right = bounding_box.to_coupled_segments(left_bounding_box,
                                                      self.right)
        if not (self.left and self.right):
            return []
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if not all_equal(event.from_left for event in events))

    def sweep(self) -> List[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine()
        min_max_x = min(to_multisegment_x_max(self.left),
                        to_multisegment_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            if event.is_right_endpoint:
                result.append(event.complement)
        return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        if not (self.left and self.right):
            return [], [], []
        left_bounding_box = bounding_box.from_multisegment(self.left)
        right_bounding_box = bounding_box.from_multisegment(self.right)
        if bounding_box.disjoint_with(left_bounding_box, right_bounding_box):
            return [], [], []
        self.left = bounding_box.to_intersecting_segments(right_bounding_box,
                                                          self.left)
        self.right = bounding_box.to_intersecting_segments(left_bounding_box,
                                                           self.right)
        if not (self.left and self.right):
            return [], [], []
        self.normalize_operands()
        multipoint = []  # type: Multipoint
        multisegment = []  # type: Multisegment
        for start, same_start_events in groupby(sorted(self.sweep(),
                                                       key=event_to_segment),
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not all_equal(event.from_left for event in same_start_events):
                no_segment_found = True
                for event, next_event in zip(same_start_events,
                                             same_start_events[1:]):
                    if (event.from_left is not next_event.from_left
                            and event.segment == next_event.segment):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            multisegment.append(event.segment)
                if no_segment_found:
                    multipoint.append(start)
        return multipoint, multisegment, []

    def sweep(self) -> List[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine()
        min_max_x = min(to_multisegment_x_max(self.left),
                        to_multisegment_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            start_x, _ = event.start
            if start_x > min_max_x:
                break
            self.process_event(event, sweep_line)
            result.append(event)
        return result


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding_box.disjoint_with(
                bounding_box.from_multisegment(self.left),
                bounding_box.from_multisegment(self.right)):
            result = self.left + self.right
            result.sort()
            return result
        self.normalize_operands()
        return sorted(segment
                      for segment, events in groupby(self.sweep(),
                                                     key=event_to_segment)
                      if all_equal(event.from_left for event in events))


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multisegment:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding_box.disjoint_with(
                bounding_box.from_multisegment(self.left),
                bounding_box.from_multisegment(self.right)):
            result = self.left + self.right
            result.sort()
            return result
        self.normalize_operands()
        return sorted(segment
                      for segment, _ in groupby(self.sweep(),
                                                key=event_to_segment))


event_to_segment = attrgetter('segment')
