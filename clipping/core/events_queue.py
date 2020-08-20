from functools import partial
from typing import (Callable,
                    cast)

from prioq.base import PriorityQueue
from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)

from .event import (BinaryEvent,
                    NaryEvent)


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
            other_end_orientation = orientation(event.start, other_event.end,
                                                event.end)
            # the lowest segment is processed first
            return (event.from_left
                    if other_end_orientation is Orientation.COLLINEAR
                    else other_end_orientation is Orientation.COUNTERCLOCKWISE)


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
                    is Orientation.COUNTERCLOCKWISE)


BinaryEventsQueue = cast(Callable[[], PriorityQueue[BinaryEvent]],
                         partial(PriorityQueue,
                                 key=BinaryEventsQueueKey))
NaryEventsQueue = cast(Callable[[], PriorityQueue[NaryEvent]],
                       partial(PriorityQueue,
                               key=NaryEventsQueueKey))
