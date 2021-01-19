from abc import (ABC,
                 abstractmethod)
from itertools import groupby
from operator import attrgetter
from typing import (Iterable,
                    List,
                    Optional,
                    Sequence,
                    Tuple,
                    Union as Union_)

from ground.base import Context
from ground.hints import (Multipolygon,
                          Point,
                          Polygon,
                          Segment)
from reprit.base import generate_repr

from . import bounding
from .event import (HoleyEvent as Event,
                    event_to_segment_endpoints,
                    events_to_connectivity)
from .events_queue import HoleyEventsQueue as EventsQueue
from .hints import (Mix,
                    SegmentEndpoints)
from .sweep_line import BinarySweepLine as SweepLine
from .utils import (all_equal,
                    endpoints_to_segments,
                    pairwise,
                    polygon_to_oriented_edges_endpoints,
                    shrink_collinear_vertices,
                    to_first_border_vertex,
                    to_polygons_x_max)


class Operation(ABC):
    __slots__ = 'context', 'left', 'right', '_events_queue'

    def __init__(self,
                 left: Sequence[Polygon],
                 right: Sequence[Polygon],
                 context: Context) -> None:
        """
        Initializes operation.

        :param left: left operand.
        :param right: right operand.
        :param context: operation context.
        """
        self.context, self.left, self.right = context, left, right
        self._events_queue = EventsQueue(context)

    __repr__ = generate_repr(__init__)

    @abstractmethod
    def compute(self) -> Union_[Mix, Multipolygon]:
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
            event.below_in_result_event = (below_event.below_in_result_event
                                           if (not self.in_result(below_event)
                                               or below_event.is_vertical)
                                           else below_event)
        event.in_result = self.in_result(event)

    def events_to_polygons(self, events: Iterable[Event]) -> Sequence[Polygon]:
        events = sorted([event for event in events if event.primary.in_result],
                        key=self._events_queue.key)
        for index, event in enumerate(events):
            event.position = index
        are_internal, depths, holes, parents = [], [], [], []
        processed = [False] * len(events)
        contour_cls = self.context.contour_cls
        contours = []
        connectivity = events_to_connectivity(events)
        for index, event in enumerate(events):
            if processed[index]:
                continue
            contour_id = len(contours)
            _compute_relations(event, contour_id, are_internal, depths, holes,
                               parents)
            vertices = _events_to_contour_vertices(event, events, contour_id,
                                                   connectivity, processed)
            shrink_collinear_vertices(vertices,
                                      context=self.context)
            if depths[contour_id] % 2:
                # holes will be in clockwise order
                vertices.reverse()
            contours.append(contour_cls(vertices))
        result = []
        polygon_cls = self.context.polygon_cls
        for index, contour in enumerate(contours):
            if are_internal[index]:
                # hole of a hole is an external polygon
                result.extend(
                        polygon_cls(contours[hole_index],
                                    [contours[hole_hole_index]
                                     for hole_hole_index in holes[hole_index]])
                        for hole_index in holes[index])
            else:
                result.append(polygon_cls(contour,
                                          [contours[hole_index]
                                           for hole_index in holes[index]]))
        return result

    def fill_queue(self) -> None:
        events_queue = self._events_queue
        for polygon in self.left:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon,
                                                        context=self.context),
                    True)
        for polygon in self.right:
            events_queue.register(
                    polygon_to_oriented_edges_endpoints(polygon,
                                                        context=self.context),
                    False)

    @abstractmethod
    def in_result(self, event: Event) -> bool:
        """Detects if event will be presented in result of the operation."""

    def normalize_operands(self) -> None:
        pass

    def process_event(self,
                      event: Event,
                      processed_events: List[Event],
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

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        sweep_line = SweepLine(self.context)
        events_queue = self._events_queue
        while events_queue:
            self.process_event(events_queue.pop(), result, sweep_line)
        return result


class Difference(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        return self.context.multipolygon_cls(self._compute())

    def in_result(self, event: Event) -> bool:
        return (event.outside
                if event.from_left
                else event.inside or event.is_common_polyline_component)

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        left_x_max = to_polygons_x_max(self.left)
        while events_queue:
            event = events_queue.pop()
            if left_x_max < event.start.x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def _compute(self) -> Sequence[Polygon]:
        if not (self.left and self.right):
            return self.left
        left_box = bounding.from_polygons(self.left,
                                          context=self.context)
        if bounding.disjoint_with(
                left_box, bounding.from_polygons(self.right,
                                                 context=self.context)):
            return self.left
        self.right = bounding.to_coupled_polygons(left_box, self.right,
                                                  context=self.context)
        if not self.right:
            return self.left
        self.normalize_operands()
        return self.events_to_polygons(self.sweep())


class CompleteIntersection(Operation):
    __slots__ = ()

    def compute(self) -> Mix:
        points, segments, polygons = self._compute()
        context = self.context
        return (context.multipoint_cls(points),
                context.multisegment_cls(segments),
                context.multipolygon_cls(polygons))

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_polygons_x_max(self.left),
                        to_polygons_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def _compute(self) -> Tuple[Sequence[Point], Sequence[Segment],
                                Sequence[Polygon]]:
        if not (self.left and self.right):
            return [], [], []
        left_box = bounding.from_polygons(self.left,
                                          context=self.context)
        right_box = bounding.from_polygons(self.right,
                                           context=self.context)
        if bounding.disjoint_with(left_box, right_box):
            return [], [], []
        self.left = bounding.to_intersecting_polygons(right_box, self.left,
                                                      context=self.context)
        self.right = bounding.to_intersecting_polygons(left_box, self.right,
                                                       context=self.context)
        if not (self.left and self.right):
            return [], [], []
        self.normalize_operands()
        events = sorted(self.sweep(),
                        key=self._events_queue.key)
        points = []  # type: List[Point]
        endpoints = []  # type: List[SegmentEndpoints]
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
                            and event.start == next_event.start
                            and event.end == next_event.end):
                        no_segment_found = False
                        if not event.is_right_endpoint:
                            endpoints.append(
                                    event_to_segment_endpoints(next_event))
                if no_segment_found and all(not event.primary.in_result
                                            for event in same_start_events):
                    points.append(start)
        return (points,
                endpoints_to_segments(endpoints,
                                      context=self.context),
                self.events_to_polygons(events))


class Intersection(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        return self.context.multipolygon_cls(self._compute())

    def in_result(self, event: Event) -> bool:
        return (event.inside
                or not event.from_left and event.is_common_region_boundary)

    def sweep(self) -> Iterable[Event]:
        self.fill_queue()
        result = []
        events_queue = self._events_queue
        sweep_line = SweepLine(self.context)
        min_max_x = min(to_polygons_x_max(self.left),
                        to_polygons_x_max(self.right))
        while events_queue:
            event = events_queue.pop()
            if min_max_x < event.start.x:
                break
            self.process_event(event, result, sweep_line)
        return result

    def _compute(self) -> Sequence[Polygon]:
        if not (self.left and self.right):
            return []
        left_box = bounding.from_polygons(self.left,
                                          context=self.context)
        right_box = bounding.from_polygons(self.right,
                                           context=self.context)
        if bounding.disjoint_with(left_box, right_box):
            return []
        self.left = bounding.to_coupled_polygons(right_box, self.left,
                                                 context=self.context)
        self.right = bounding.to_coupled_polygons(left_box, self.right,
                                                  context=self.context)
        if not (self.left and self.right):
            return []
        self.normalize_operands()
        return self.events_to_polygons(self.sweep())


class SymmetricDifference(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        return self.context.multipolygon_cls(self._compute())

    def in_result(self, event: Event) -> bool:
        return not event.is_overlap

    def _compute(self) -> Sequence[Polygon]:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding.disjoint_with(
                bounding.from_polygons(self.left,
                                       context=self.context),
                bounding.from_polygons(self.right,
                                       context=self.context)):
            result = []
            result += self.left
            result += self.right
            result.sort(key=to_first_border_vertex)
            return result
        self.normalize_operands()
        return self.events_to_polygons(self.sweep())


class Union(Operation):
    __slots__ = ()

    def compute(self) -> Multipolygon:
        return self.context.multipolygon_cls(self._compute())

    def _compute(self) -> Sequence[Polygon]:
        if not (self.left and self.right):
            return self.left or self.right
        elif bounding.disjoint_with(
                bounding.from_polygons(self.left,
                                       context=self.context),
                bounding.from_polygons(self.right,
                                       context=self.context)):
            result = []
            result += self.left
            result += self.right
            result.sort(key=to_first_border_vertex)
            return result
        self.normalize_operands()
        return self.events_to_polygons(self.sweep())

    def in_result(self, event: Event) -> bool:
        return (event.outside
                or not event.from_left and event.is_common_region_boundary)


def _compute_relations(event: Event,
                       contour_id: int,
                       are_internal: List[bool],
                       depths: List[int],
                       holes: List[List[int]],
                       parents: List[Optional[int]]) -> None:
    depth = 0
    parent = None
    is_internal = False
    below_in_result_event = event.below_in_result_event
    if below_in_result_event is not None:
        below_in_result_contour_id = below_in_result_event.contour_id
        if not below_in_result_event.result_in_out:
            holes[below_in_result_contour_id].append(contour_id)
            parent = below_in_result_contour_id
            depth = depths[below_in_result_contour_id] + 1
            is_internal = True
        elif are_internal[below_in_result_contour_id]:
            below_in_result_parent_id = parents[below_in_result_contour_id]
            holes[below_in_result_parent_id].append(contour_id)
            parent = below_in_result_parent_id
            depth = depths[below_in_result_contour_id]
            is_internal = True
    holes.append([])
    parents.append(parent)
    depths.append(depth)
    are_internal.append(is_internal)


def _events_to_contour_vertices(cursor: Event,
                                events: Sequence[Event],
                                contour_id: int,
                                connectivity: Sequence[int],
                                processed: List[bool]) -> List[Point]:
    contour_start = cursor.start
    contour = [contour_start]
    contour_events = [cursor]
    complement_position = cursor.complement.position
    vertices_positions = {contour_start: 0}
    while cursor.end != contour_start:
        vertex = cursor.end
        if vertex in vertices_positions:
            # vertices loop found, i.e. contour has self-intersection
            previous_vertex_position = vertices_positions[vertex]
            del contour[previous_vertex_position:]
            del contour_events[previous_vertex_position:]
        else:
            vertices_positions[vertex] = len(contour)
        contour.append(vertex)
        position = _to_next_position(complement_position, processed,
                                     connectivity)
        if position is None:
            break
        cursor = events[position]
        contour_events.append(cursor)
        complement_position = cursor.complement.position
    for event in contour_events:
        processed[event.position] = processed[event.complement.position] = True
        if event.is_right_endpoint:
            event.complement.result_in_out = True
            event.complement.contour_id = contour_id
        else:
            event.result_in_out = False
            event.contour_id = contour_id
    return contour


def _to_next_position(position: int,
                      processed: Sequence[bool],
                      connectivity: Sequence[int]) -> Optional[int]:
    candidate = position
    while True:
        candidate = connectivity[candidate]
        if not processed[candidate]:
            return candidate
        elif candidate == position:
            return None
