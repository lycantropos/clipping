from functools import singledispatch
from typing import (Any,
                    Callable,
                    Iterable,
                    Sequence,
                    Tuple,
                    TypeVar,
                    Union)

from ground.base import (Orientation,
                         Relation,
                         get_context)
from ground.hints import Shaped
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from orient.planar import multisegment_in_multisegment

from clipping.core.utils import to_endpoints
from clipping.hints import (Multiregion,
                            Region)

Strategy = SearchStrategy
Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
_context = get_context()
EMPTY = _context.empty
Box = _context.box_cls
Contour = _context.contour_cls
Empty = _context.empty_cls
Mix = _context.mix_cls
Multipoint = _context.multipoint_cls
Multipolygon = _context.multipolygon_cls
Multisegment = _context.multisegment_cls
Point = _context.point_cls
Polygon = _context.polygon_cls
Segment = _context.segment_cls
BoxesPair = Tuple[Box, Box]
BoxesTriplet = Tuple[Box, Box, Box]
MultisegmentsPair = Tuple[Multisegment, Multisegment]
MultisegmentsTriplet = Tuple[Multisegment, Multisegment, Multisegment]
MultipolygonWithMultisegment = Tuple[Multipolygon, Multisegment]
MultiregionsPair = Tuple[Multiregion, Multiregion]
PolygonWithMultisegment = Tuple[Polygon, Multisegment]
PolygonWithSegment = Tuple[Polygon, Segment]
RegionsPair = Tuple[Region, Region]
PolygonsPair = Tuple[Polygon, Polygon]
PolygonsTriplet = Tuple[Polygon, Polygon, Polygon]
SegmentsPair = Tuple[Segment, Segment]
SegmentsTriplet = Tuple[Segment, Segment, Segment]
segments_intersection = _context.segments_intersection
segments_relation = _context.segments_relation


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def arg_min(values: Sequence[Domain]) -> int:
    return min(range(len(values)),
               key=values.__getitem__)


@singledispatch
def are_compounds_similar(left: Domain, right: Domain) -> bool:
    raise TypeError('Unsupported object type: {!r}.'
                    .format(type(left)))


@are_compounds_similar.register(Empty)
def _(left: Empty, right: Empty) -> bool:
    return left is right


@are_compounds_similar.register(Mix)
def _(left: Mix, right: Mix) -> bool:
    return (are_compounds_similar(left.discrete, right.discrete)
            and are_compounds_similar(left.linear, right.linear)
            and are_compounds_similar(left.shaped, right.shaped))


@are_compounds_similar.register(Multipoint)
def _(left: Multipoint, right: Multipoint) -> bool:
    return (len(left.points) == len(right.points)
            and set(left.points) == set(right.points))


@are_compounds_similar.register(Multipolygon)
def _(left: Multipolygon, right: Multipolygon) -> bool:
    return normalize_multipolygon(left) == normalize_multipolygon(right)


@are_compounds_similar.register(Multisegment)
def _(left: Multisegment, right: Multisegment) -> bool:
    return (len(left.segments) == len(right.segments)
            and (frozenset(map(to_endpoints,
                               map(to_sorted_segment, left.segments)))
                 == frozenset(map(to_endpoints,
                                  map(to_sorted_segment, right.segments)))))


@are_compounds_similar.register(Polygon)
def _(left: Polygon, right: Polygon) -> bool:
    return normalize_polygon(left) == normalize_polygon(right)


@are_compounds_similar.register(Segment)
def _(left: Segment, right: Segment) -> bool:
    return {left.start, left.end} == {right.start, right.end}


def are_multisegments_equivalent(left: Multisegment,
                                 right: Multisegment) -> bool:
    return (not (left.segments or right.segments)
            or multisegment_in_multisegment(left, right) is Relation.EQUAL)


def is_polygon_similar_to_region(polygon: Polygon, region: Region) -> bool:
    return are_compounds_similar(polygon, Polygon(region, []))


def are_segments_sequences_similar(left: Sequence[Segment],
                                   right: Sequence[Segment]) -> bool:
    return (normalize_segments_sequence(left)
            == normalize_segments_sequence(right))


def normalize_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    polygons = [normalize_polygon(polygon)
                for polygon in multipolygon.polygons]
    polygons.sort(key=lambda polygon: polygon.border.vertices[0])
    return Multipolygon(polygons)


def normalize_polygon(polygon: Polygon) -> Polygon:
    return Polygon(normalize_region(polygon.border),
                   normalize_regions(polygon.holes))


def normalize_regions(multiregion: Multiregion) -> Multiregion:
    result = [normalize_region(region) for region in multiregion]
    result.sort(key=lambda region: region.vertices[:2])
    return result


def normalize_region(contour: Contour) -> Contour:
    return Contour(_to_counterclockwise_vertices(
            rotate_sequence(contour.vertices,
                            arg_min(contour.vertices))))


def normalize_segments_sequence(segments: Sequence[Segment]
                                ) -> Sequence[Segment]:
    return sorted([to_sorted_segment(segment) for segment in segments],
                  key=to_endpoints)


def reverse_sequence(sequence: Domain) -> Domain:
    return sequence[::-1]


def rotate_sequence(sequence: Domain, index: int) -> Domain:
    return sequence[index:] + sequence[:index]


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def to_triplets(strategy: Strategy[Domain]
                ) -> Strategy[Tuple[Domain, Domain, Domain]]:
    return strategies.tuples(strategy, strategy, strategy)


contour_to_edges = _context.contour_edges
is_contour = Contour.__instancecheck__


def is_holeless_compound(object_: Any) -> bool:
    return (is_compound(object_)
            and (not is_shaped(object_) or not shaped_has_holes(object_))
            and (not is_mix(object_) or not shaped_has_holes(object_.shaped)))


def shaped_has_holes(shaped: Shaped) -> bool:
    return (bool(shaped.holes)
            if is_polygon(shaped)
            else any(polygon.holes for polygon in shaped.polygons))


def is_linear(object_: Any) -> bool:
    return isinstance(object_, (Multisegment, Segment))


def is_maybe_linear(object_: Any) -> bool:
    return is_empty(object_) or is_linear(object_)


def is_non_shaped(object_: Any) -> bool:
    return (is_homogeneous_non_shaped(object_)
            or isinstance(object_, Mix) and is_empty(object_.shaped))


def is_homogeneous_non_shaped(object_: Any) -> bool:
    return (is_empty(object_)
            or isinstance(object_, (Multipoint, Multisegment, Segment)))


def is_compound(object_: Any) -> bool:
    return (is_empty(object_)
            or isinstance(object_, (Mix, Multipoint, Multipolygon,
                                    Multisegment, Polygon, Segment)))


def is_maybe_shaped(object_: Any) -> bool:
    return is_empty(object_) or is_shaped(object_)


def is_shaped(object_: Any) -> bool:
    return isinstance(object_, (Multipolygon, Polygon))


def is_empty(object_: Any) -> bool:
    return object_ is EMPTY


is_mix = Mix.__instancecheck__
is_multipoint = Multipoint.__instancecheck__
is_multisegment = Multisegment.__instancecheck__
is_polygon = Polygon.__instancecheck__
is_region = is_contour
is_segment = Segment.__instancecheck__


def compound_to_linear(object_: Any) -> Any:
    if is_empty(object_) or is_multipoint(object_) or is_shaped(object_):
        return EMPTY
    elif is_mix(object_):
        return object_.linear
    else:
        return object_


def compound_to_shaped(object_: Any) -> Any:
    if is_non_shaped(object_):
        return EMPTY
    elif is_mix(object_):
        return object_.shaped
    else:
        return object_


def reverse_contour(contour: Contour) -> Contour:
    return Contour(reverse_sequence(contour.vertices))


def reverse_contour_coordinates(contour: Contour) -> Contour:
    return Contour([reverse_point_coordinates(vertex)
                    for vertex in contour.vertices])


@singledispatch
def reverse_compound_coordinates(compound: Domain) -> Domain:
    raise TypeError('Unsupported object type: {!r}.'
                    .format(type(compound)))


@reverse_compound_coordinates.register(Empty)
def _(compound: Empty) -> Empty:
    return compound


@reverse_compound_coordinates.register(Mix)
def _(compound: Mix) -> Mix:
    return type(compound)(reverse_compound_coordinates(compound.discrete),
                          reverse_compound_coordinates(compound.linear),
                          reverse_compound_coordinates(compound.shaped))


@reverse_compound_coordinates.register(Multipoint)
def _(multipoint: Multipoint) -> Multipoint:
    return Multipoint([reverse_point_coordinates(point)
                       for point in multipoint.points])


@reverse_compound_coordinates.register(Multipolygon)
def reverse_multipolygon_coordinates(multipolygon: Multipolygon
                                     ) -> Multipolygon:
    return Multipolygon([reverse_polygon_coordinates(polygon)
                         for polygon in multipolygon.polygons])


def reverse_polygon_border(polygon: Polygon) -> Polygon:
    return Polygon(reverse_region(polygon.border), polygon.holes)


def reverse_polygon_holes(polygon: Polygon) -> Polygon:
    return Polygon(polygon.border, reverse_multiregion(polygon.holes))


def reverse_polygon_holes_contours(polygon: Polygon) -> Polygon:
    return Polygon(polygon.border,
                   [reverse_region(hole) for hole in polygon.holes])


reverse_multiregion = reverse_sequence


def reverse_regions_coordinates(multiregion: Multiregion) -> Multiregion:
    return [reverse_region_coordinates(region) for region in multiregion]


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return Multisegment(reverse_sequence(multisegment.segments))


@reverse_compound_coordinates.register(Multisegment)
def reverse_multisegment_coordinates(multisegment: Multisegment
                                     ) -> Multisegment:
    return Multisegment(reverse_segments_sequence_coordinates(
            multisegment.segments))


def reverse_multisegment_endpoints(multisegment: Multisegment) -> Multisegment:
    return Multisegment(reverse_segments_sequence_endpoints(
            multisegment.segments))


def reverse_point_coordinates(point: Point) -> Point:
    return Point(point.y, point.x)


@reverse_compound_coordinates.register(Polygon)
def reverse_polygon_coordinates(polygon: Polygon) -> Polygon:
    return Polygon(reverse_contour_coordinates(polygon.border),
                   reverse_regions_coordinates(polygon.holes))


reverse_region = reverse_contour
reverse_region_coordinates = reverse_contour_coordinates


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)


@reverse_compound_coordinates.register(Segment)
def reverse_segment_coordinates(segment: Segment) -> Segment:
    return Segment(reverse_point_coordinates(segment.start),
                   reverse_point_coordinates(segment.end))


reverse_segments_sequence = reverse_sequence


def reverse_segments_sequence_coordinates(segments: Sequence[Segment]
                                          ) -> Sequence[Segment]:
    return [reverse_segment_coordinates(segment) for segment in segments]


def reverse_segments_sequence_endpoints(segments: Sequence[Segment]
                                        ) -> Sequence[Segment]:
    return [reverse_segment(segment) for segment in segments]


def to_sorted_segment(segment: Segment) -> Segment:
    return segment if segment.start < segment.end else reverse_segment(segment)


def pack_non_shaped(object_: Union[Empty, Mix, Multipoint, Multisegment,
                                   Segment]
                    ) -> Tuple[Sequence[Point], Sequence[Segment]]:
    if object_ is EMPTY:
        return [], []
    elif isinstance(object_, Mix):
        discrete_points, _ = pack_non_shaped(object_.discrete)
        _, linear_segments = pack_non_shaped(object_.linear)
        return discrete_points, linear_segments
    elif isinstance(object_, Multipoint):
        return object_.points, []
    elif isinstance(object_, Multisegment):
        return [], object_.segments
    elif isinstance(object_, Segment):
        return [], [object_]
    else:
        raise TypeError('Unsupported object type: {!r}.'.format(type(object_)))


def segments_intersections(first: Segment, second: Segment
                           ) -> Tuple[Point, ...]:
    first_start, first_end = first.start, first.end
    second_start, second_end = second.start, second.end
    relation = segments_relation(first, second)
    if relation is Relation.DISJOINT:
        return ()
    elif relation is Relation.CROSS or relation is Relation.TOUCH:
        return segments_intersection(first, second),
    else:
        _, first_point, second_point, _ = sorted([first_start, first_end,
                                                  second_start, second_end])
        return first_point, second_point


def to_polygon_contours(polygon: Polygon) -> Iterable[Contour]:
    yield polygon.border
    yield from polygon.holes


def _to_counterclockwise_vertices(vertices: Sequence[Point]
                                  ) -> Sequence[Point]:
    if _to_first_angle_orientation(vertices) is not Orientation.CLOCKWISE:
        vertices = vertices[:1] + vertices[1:][::-1]
    return vertices


def _to_first_angle_orientation(vertices: Sequence[Point]) -> Orientation:
    return _context.angle_orientation(vertices[0], vertices[-1], vertices[1])
