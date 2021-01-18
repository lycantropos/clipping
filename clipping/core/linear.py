from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    Sequence,
                    Union as Union_)

from ground.base import Context
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
                    to_multisegment_x_max)


def merge_segments(segments: Sequence[Segment],
                   *,
                   context: Context) -> Iterable[Segment]:
    if not segments:
        return
    events_queue = NaryEventsQueue()
    events_queue.register_segments(segments)
    sweep_line = NarySweepLine(context)
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
    __slots__ = 'context', 'left', 'right', '_events_queue'

    def __init__(self,
                 left: Multisegment,
                 right: Multisegment,
                 context: Context) -> None:
        """
        Initializes operation.

        :param left: left operand.
        :param right: right operand.
        :param context: operation context.
        """
        self.context, self.left, self.right = context, left, right
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
        pass

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

    def sweep(self) -> Iterable[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
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

    def sweep(self) -> Iterable[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
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

    def sweep(self) -> Sequence[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
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

    def sweep(self) -> Sequence[BinaryEvent]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = BinarySweepLine(self.context)
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
