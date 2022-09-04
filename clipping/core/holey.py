from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Union as Union_)

from ground.base import Context
from ground.hints import (Contour,
                          Empty,
                          Mix,
                          Multipoint,
                          Multipolygon,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment)
from reprit.base import generate_repr

from . import bounding
from .event import (UNDEFINED_INDEX,
                    LeftHoleyEvent as LeftEvent,
                    RightShapedEvent as RightEvent,
                    events_to_connectivity)
from .events_queue import HoleyEventsQueue as EventsQueue
from .hints import Orienteer
from .operands import HoleyOperand
from .sweep_line import BinarySweepLine as SweepLine
from .unpacking import (unpack_mix,
                        unpack_points,
                        unpack_polygons,
                        unpack_segments)
from .utils import (all_equal,
                    endpoints_to_segments,
                    polygon_to_oriented_edges_endpoints,
                    shrink_collinear_vertices,
                    to_endpoints,
                    to_first_border_vertex,
                    to_polygons_x_max)

Event = Union_[LeftEvent, RightEvent]


class Operation(ABC):
    __slots__ = 'context', 'first', 'second', '_events_queue'

    def __init__(self,
                 first: HoleyOperand,
                 second: HoleyOperand,
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
    def compute(self) -> Union_[Mix, Multipolygon]:
        """
        Computes result of the operation.
        """

    def compute_fields(self, event: LeftEvent, below_event: Optional[LeftEvent]
                       ) -> None:
        if below_event is not None:
            event.other_interior_to_left = (
                below_event.other_interior_to_left
                if event.from_first_operand is below_event.from_first_operand
                else below_event.interior_to_left
            )
            event.below_event_from_shaped_result = (
                below_event.below_event_from_shaped_result
                if (not self.from_shaped_result(below_event)
                    or below_event.is_vertical)
                else below_event
            )
        event.from_shaped_result = self.from_shaped_result(event)

    def events_to_polygons(self, events: Sequence[Event]) -> Sequence[Polygon]:
        events = [event
                  for event in events
                  if event.primary.from_shaped_result]
        if not events:
            return []
        max_endpoint_id = events[-1].start_id
        assert max_endpoint_id != UNDEFINED_INDEX
        assert all(event.start_id <= max_endpoint_id for event in events)
        events.sort(key=self._events_queue.key)
        for event_id, event in enumerate(events):
            event.id = event_id
        are_internal, depths, holes, parents = [], [], [], []
        are_events_processed = [False] * len(events)
        context = self.context
        contour_cls, orienteer = context.contour_cls, context.angle_orientation
        contours = []  # type: List[Contour]
        connectivity = events_to_connectivity(events)
        visited_endpoints_positions = [UNDEFINED_INDEX] * (max_endpoint_id + 1)
        for event_id, event in enumerate(events):
            if are_events_processed[event_id]:
                continue
            contour_id = len(contours)
            _compute_relations(event, contour_id, are_internal, depths, holes,
                               parents)
            contour_events = _to_contour_events(event, events, connectivity,
                                                are_events_processed,
                                                visited_endpoints_positions)
            _process_contour_events(contour_events, contour_id,
                                    are_events_processed)
            vertices = _contour_events_to_vertices(contour_events, orienteer)
            if depths[contour_id] % 2:
                # holes will be in clockwise order
                vertices[:] = vertices[:1] + vertices[:0:-1]
            contours.append(contour_cls(vertices))
        result = []
        polygon_cls = context.polygon_cls
        for contour_id, contour in enumerate(contours):
            if are_internal[contour_id]:
                # hole of a hole is an external polygon
                result.extend(polygon_cls(contours[hole_id],
                                          [contours[hole_hole_id]
                                           for hole_hole_id in holes[hole_id]])
                              for hole_id in holes[contour_id])
            else:
                result.append(polygon_cls(contour,
                                          [contours[hole_id]
                                           for hole_id in holes[contour_id]]))
        return result

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        for polygon in self.first.polygons:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon, self.context),
                    True
            )
        for polygon in self.second.polygons:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon, self.context),
                    False
            )

    @abstractmethod
    def from_shaped_result(self, event: LeftEvent) -> bool:
        """Detects if event is a part of resulting shaped geometry."""

    def process_event(self,
                      event: Event,
                      processed_events: List[Event],
                      sweep_line: SweepLine) -> None:
        if not event.is_left:
            opposite_event = event.left
            if opposite_event in sweep_line:
                above_event, below_event = (sweep_line.above(opposite_event),
                                            sweep_line.below(opposite_event))
                sweep_line.remove(opposite_event)
                if above_event is not None and below_event is not None:
                    self._events_queue.detect_intersection(below_event,
                                                           above_event)
            processed_events.append(event)
        elif event not in sweep_line:
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
            processed_events.append(event)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine(self.context)
        events_queue = self._events_queue
        event = events_queue.pop()
        current_endpoint = event.start
        current_endpoint_id = event.start_id = 0
        self.process_event(event, result, sweep_line)
        while events_queue:
            event = events_queue.pop()
            if event.start != current_endpoint:
                current_endpoint = event.start
                current_endpoint_id += 1
            event.start_id = current_endpoint_id
            self.process_event(event, result, sweep_line)
        return result


def _contour_events_to_vertices(events: Sequence[Event],
                                orienteer: Orienteer) -> List[Point]:
    result = [events[0].start] + [event.end for event in events[:-1]]
    shrink_collinear_vertices(result, orienteer)
    return result


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Mix, Multipoint, Multipolygon,
                                Multisegment, Polygon, Segment]:
        context = self.context
        first_box, second_box = (context.polygons_box(self.first.polygons),
                                 context.polygons_box(self.second.polygons))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.polygons = bounding.to_intersecting_polygons(
                second_box, self.first.polygons, context)
        if not self.first.polygons:
            return context.empty
        self.second.polygons = bounding.to_intersecting_polygons(
                first_box, self.second.polygons, context
        )
        if not self.second.polygons:
            return context.empty
        events = sorted(self.sweep(),
                        key=self._events_queue.key)
        points = []  # type: List[Point]
        for start, same_start_events in groupby(events,
                                                key=attrgetter('start')):
            same_start_events = list(same_start_events)
            if not (any(event.primary.wholly_in_complete_intersection
                        for event in same_start_events)
                    or all_equal(event.from_first_operand
                                 for event in same_start_events)):
                points.append(start)
        segments = endpoints_to_segments(
                [to_endpoints(event)
                 for event in events
                 if (event.is_left
                     and event.from_first_operand
                     and event.is_common_polyline_component)],
                context
        )
        polygons = self.events_to_polygons(events)
        return unpack_mix(unpack_points(points, context),
                          unpack_segments(segments, context),
                          unpack_polygons(polygons, context), context)

    def from_shaped_result(self, event: LeftEvent) -> bool:
        return (event.inside
                or (not event.from_first_operand
                    and event.is_common_region_boundary))

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_polygons_x_max(self.first.polygons),
                        to_polygons_x_max(self.second.polygons))
        event = events_queue.pop()
        current_endpoint = event.start
        current_endpoint_id = event.start_id = 0
        self.process_event(event, result, sweep_line)
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            if event.start != current_endpoint:
                current_endpoint = event.start
                current_endpoint_id += 1
            event.start_id = current_endpoint_id
            self.process_event(event, result, sweep_line)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Multipolygon, Polygon]:
        context = self.context
        first_box = context.polygons_box(self.first.polygons)
        if bounding.disjoint_with(first_box,
                                  context.polygons_box(self.second.polygons)):
            return self.first.value
        self.second.polygons = bounding.to_coupled_polygons(
                first_box, self.second.polygons, context
        )
        return (unpack_polygons(self.events_to_polygons(self.sweep()), context)
                if self.second.polygons
                else self.first.value)

    def from_shaped_result(self, event: LeftEvent) -> bool:
        return (event.outside
                if event.from_first_operand
                else event.inside or event.is_common_polyline_component)

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        first_x_max = to_polygons_x_max(self.first.polygons)
        event = events_queue.pop()
        current_endpoint = event.start
        current_endpoint_id = event.start_id = 0
        self.process_event(event, result, sweep_line)
        while events_queue:
            event = events_queue.pop()
            if first_x_max < event.start.x:
                break
            if event.start != current_endpoint:
                current_endpoint = event.start
                current_endpoint_id += 1
            event.start_id = current_endpoint_id
            self.process_event(event, result, sweep_line)
        return result


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Multipolygon, Polygon]:
        context = self.context
        first_box, second_box = (context.polygons_box(self.first.polygons),
                                 context.polygons_box(self.second.polygons))
        if bounding.disjoint_with(first_box, second_box):
            return context.empty
        self.first.polygons = bounding.to_coupled_polygons(
                second_box, self.first.polygons, context
        )
        if not self.first.polygons:
            return context.empty
        self.second.polygons = bounding.to_coupled_polygons(
                first_box, self.second.polygons, context
        )
        return (unpack_polygons(self.events_to_polygons(self.sweep()), context)
                if self.second.polygons
                else context.empty)

    def from_shaped_result(self, event: LeftEvent) -> bool:
        return (event.inside
                or (not event.from_first_operand
                    and event.is_common_region_boundary))

    def sweep(self) -> List[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_polygons_x_max(self.first.polygons),
                        to_polygons_x_max(self.second.polygons))
        event = events_queue.pop()
        current_endpoint = event.start
        current_endpoint_id = event.start_id = 0
        self.process_event(event, result, sweep_line)
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            if event.start != current_endpoint:
                current_endpoint = event.start
                current_endpoint_id += 1
            event.start_id = current_endpoint_id
            self.process_event(event, result, sweep_line)
        return result


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Empty, Multipolygon, Polygon]:
        context = self.context
        if bounding.disjoint_with(context.polygons_box(self.first.polygons),
                                  context.polygons_box(self.second.polygons)):
            polygons = []
            polygons += self.first.polygons
            polygons += self.second.polygons
            polygons.sort(key=to_first_border_vertex)
            return context.multipolygon_cls(polygons)
        return unpack_polygons(self.events_to_polygons(self.sweep()), context)

    def from_shaped_result(self, event: LeftEvent) -> bool:
        return not event.is_overlap


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Union_[Multipolygon, Polygon]:
        context = self.context
        if bounding.disjoint_with(context.polygons_box(self.first.polygons),
                                  context.polygons_box(self.second.polygons)):
            polygons = []
            polygons += self.first.polygons
            polygons += self.second.polygons
            polygons.sort(key=to_first_border_vertex)
            return context.multipolygon_cls(polygons)
        return unpack_polygons(self.events_to_polygons(self.sweep()), context)

    def from_shaped_result(self, event: LeftEvent) -> bool:
        return (event.outside
                or not event.from_first_operand and event.is_common_region_boundary)


def _compute_relations(event: LeftEvent,
                       contour_id: int,
                       are_internal: List[bool],
                       depths: List[int],
                       holes: List[List[int]],
                       parents: List[Optional[int]]) -> None:
    depth = 0
    parent = None
    is_internal = False
    below_event_from_shaped_result = event.below_event_from_shaped_result
    if below_event_from_shaped_result is not None:
        below_contour_id = below_event_from_shaped_result.contour_id
        if not below_event_from_shaped_result.from_in_to_out:
            if not are_internal[below_contour_id]:
                holes[below_contour_id].append(contour_id)
                parent = below_contour_id
                depth = depths[below_contour_id] + 1
                is_internal = True
        elif are_internal[below_contour_id]:
            below_in_result_parent_id = parents[below_contour_id]
            holes[below_in_result_parent_id].append(contour_id)
            parent = below_in_result_parent_id
            depth = depths[below_contour_id]
            is_internal = True
    holes.append([])
    parents.append(parent)
    depths.append(depth)
    are_internal.append(is_internal)


def _to_contour_events(event: LeftEvent,
                       events: Sequence[Event],
                       connectivity: Sequence[int],
                       are_events_processed: Sequence[bool],
                       visited_endpoints_positions: List[int]) -> List[Event]:
    assert event.is_left
    result = [event]
    visited_endpoints_positions[event.start_id] = 0
    opposite_event_id = event.right.id
    contour_start = event.start
    cursor = event
    visited_endpoints_ids = [event.start_id]
    while cursor.end != contour_start:
        previous_endpoint_position = visited_endpoints_positions[cursor.end_id]
        if previous_endpoint_position == UNDEFINED_INDEX:
            visited_endpoints_positions[cursor.end_id] = len(result)
        else:
            # vertices loop found, i.e. contour has self-intersection
            assert previous_endpoint_position != 0
            for loop_event in result[previous_endpoint_position:]:
                visited_endpoints_positions[
                    loop_event.end_id
                ] = UNDEFINED_INDEX
            del result[previous_endpoint_position:]
        visited_endpoints_ids.append(cursor.end_id)
        event_id = _to_next_event_id(opposite_event_id, are_events_processed,
                                     connectivity)
        if event_id == UNDEFINED_INDEX:
            break
        cursor = events[event_id]
        opposite_event_id = cursor.opposite.id
        result.append(cursor)
    for event_id in visited_endpoints_ids:
        visited_endpoints_positions[event_id] = UNDEFINED_INDEX
    assert all(position == UNDEFINED_INDEX
               for position in visited_endpoints_positions)
    return result


def _process_contour_events(contour_events: Iterable[Event],
                            contour_id: int,
                            are_events_processed: List[bool]) -> None:
    for event in contour_events:
        are_events_processed[event.id] = True
        are_events_processed[event.opposite.id] = True
        if event.is_left:
            event.from_in_to_out = False
            event.contour_id = contour_id
        else:
            event.opposite.from_in_to_out = True
            event.opposite.contour_id = contour_id


def _to_next_event_id(event_id: int,
                      are_events_processed: Sequence[bool],
                      connectivity: Sequence[int]) -> int:
    candidate = event_id
    while True:
        candidate = connectivity[candidate]
        if not are_events_processed[candidate]:
            return candidate
        elif candidate == event_id:
            return UNDEFINED_INDEX
