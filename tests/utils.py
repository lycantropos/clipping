from typing import (Any,
                    Callable,
                    Iterable,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.base import (Orientation,
                         Relation,
                         get_context)
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from orient.planar import multisegment_in_multisegment

from clipping.core.linear import segment_to_endpoints
from clipping.hints import (HolelessMix,
                            LinearMix,
                            Mix,
                            Multiregion)

Strategy = SearchStrategy
Domain = TypeVar('Domain')
Key = Callable[[Domain], Any]
_context = get_context()
Box = _context.box_cls
Contour = _context.contour_cls
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
MultiregionsTriplet = Tuple[Multiregion, Multiregion, Multiregion]
MultipolygonsPair = Tuple[Multipolygon, Multipolygon]
MultipolygonsTriplet = Tuple[Multipolygon, Multipolygon, Multipolygon]
segments_intersection = _context.segments_intersection
segments_relation = _context.segments_relation


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def arg_min(values: Sequence[Domain]) -> int:
    return min(range(len(values)),
               key=values.__getitem__)


def linear_mix_equivalent_to_multisegment(mix: LinearMix,
                                          other: Multisegment) -> bool:
    multipoint, multisegment = mix
    return (not multipoint.points
            and are_multisegments_equivalent(multisegment, other))


def mix_similar_to_multipolygon(mix: Mix, other: Multipolygon) -> bool:
    multipoint, multisegment, multipolygon = mix
    return (not multipoint.points and not multisegment.segments
            and are_multipolygons_similar(multipolygon, other))


def holeless_mix_similar_to_multiregion(mix: HolelessMix,
                                        other: Multiregion) -> bool:
    multipoint, multisegment, multiregion = mix
    return (not multipoint.points and not multisegment.segments
            and are_multiregions_similar(multiregion, other))


def are_holeless_mixes_similar(left: HolelessMix, right: HolelessMix) -> bool:
    left_multipoint, left_multisegment, left_multiregion = left
    right_multipoint, right_multisegment, right_multiregion = right
    return (are_multipoints_similar(left_multipoint, right_multipoint)
            and are_multisegments_similar(left_multisegment,
                                          right_multisegment)
            and are_multiregions_similar(left_multiregion, right_multiregion))


def are_linear_mixes_similar(left: LinearMix, right: LinearMix) -> bool:
    left_multipoint, left_multisegment = left
    right_multipoint, right_multisegment = right
    return (are_multipoints_similar(left_multipoint, right_multipoint)
            and are_multisegments_similar(left_multisegment,
                                          right_multisegment))


def are_mixes_similar(left: Mix, right: Mix) -> bool:
    left_multipoint, left_multisegment, left_multipolygon = left
    right_multipoint, right_multisegment, right_multipolygon = right
    return (are_multipoints_similar(left_multipoint, right_multipoint)
            and are_multisegments_similar(left_multisegment,
                                          right_multisegment)
            and are_multipolygons_similar(left_multipolygon,
                                          right_multipolygon))


def are_multipoints_similar(left: Multipoint, right: Multipoint) -> bool:
    return (len(left.points) == len(right.points)
            and set(left.points) == set(right.points))


def are_multisegments_equivalent(left: Multisegment,
                                 right: Multisegment) -> bool:
    return (not (left.segments or right.segments)
            or multisegment_in_multisegment(left, right) is Relation.EQUAL)


def are_multisegments_similar(left: Multisegment, right: Multisegment) -> bool:
    return (len(left.segments) == len(right.segments)
            and (frozenset(map(segment_to_endpoints,
                               map(to_sorted_segment, left.segments)))
                 == frozenset(map(segment_to_endpoints,
                                  map(to_sorted_segment, right.segments)))))


def are_multipolygons_similar(left: Multipolygon, right: Multipolygon) -> bool:
    return normalize_multipolygon(left) == normalize_multipolygon(right)


def are_multiregions_similar(left: Multiregion, right: Multiregion) -> bool:
    return normalize_multiregion(left) == normalize_multiregion(right)


def are_segments_sequences_similar(left: Sequence[Segment],
                                   right: Sequence[Segment]) -> bool:
    return (normalize_segments_sequence(left)
            == normalize_segments_sequence(right))


def normalize_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    polygons = [Polygon(normalize_region(polygon.border),
                        normalize_multiregion(polygon.holes))
                for polygon in multipolygon.polygons]
    polygons.sort(key=lambda polygon: polygon.border.vertices[0])
    return Multipolygon(polygons)


def normalize_multiregion(multiregion: Multiregion) -> Multiregion:
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
                  key=segment_to_endpoints)


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


def is_holeless_mix(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 3
            and is_multipoint(object_[0])
            and is_multisegment(object_[1])
            and is_multiregion(object_[2]))


def is_linear_mix(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 2
            and is_multipoint(object_[0])
            and is_multisegment(object_[1]))


def is_linear_mix_empty(mix: LinearMix) -> bool:
    multipoint, multisegment = mix
    return not (multipoint.points or multisegment.segments)


def is_mix(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 3
            and is_multipoint(object_[0])
            and is_multisegment(object_[1])
            and is_multipolygon(object_[2]))


is_multipoint = Multipoint.__instancecheck__
is_multipolygon = Multipolygon.__instancecheck__


def is_multiregion(object_: Any) -> bool:
    return isinstance(object_, list) and all(map(is_region, object_))


is_multisegment = Multisegment.__instancecheck__
is_region = is_contour


def reverse_contour(contour: Contour) -> Contour:
    return Contour(reverse_sequence(contour.vertices))


def reverse_contour_coordinates(contour: Contour) -> Contour:
    return Contour([reverse_point_coordinates(vertex)
                    for vertex in contour.vertices])


def reverse_holeless_mix_coordinates(mix: HolelessMix) -> HolelessMix:
    multipoint, multisegment, multiregion = mix
    return (reverse_multipoint_coordinates(multipoint),
            reverse_multisegment_coordinates(multisegment),
            reverse_multiregion_coordinates(multiregion))


def reverse_mix_coordinates(mix: Mix) -> Mix:
    multipoint, multisegment, multipolygon = mix
    return (reverse_multipoint_coordinates(multipoint),
            reverse_multisegment_coordinates(multisegment),
            reverse_multipolygon_coordinates(multipolygon))


def reverse_linear_mix_coordinates(mix: LinearMix) -> LinearMix:
    multipoint, multisegment = mix
    return (reverse_multipoint_coordinates(multipoint),
            reverse_multisegment_coordinates(multisegment))


def reverse_multipoint_coordinates(multipoint: Multipoint) -> Multipoint:
    return Multipoint([reverse_point_coordinates(point)
                       for point in multipoint.points])


def reverse_multipolygon(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon(multipolygon.polygons[::-1])


def reverse_multipolygon_borders(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon([Polygon(reverse_region(polygon.border),
                                 polygon.holes)
                         for polygon in multipolygon.polygons])


def reverse_multipolygon_coordinates(multipolygon: Multipolygon
                                     ) -> Multipolygon:
    return Multipolygon([reverse_polygon_coordinates(polygon)
                         for polygon in multipolygon.polygons])


def reverse_multipolygon_holes(multipolygon: Multipolygon) -> Multipolygon:
    return Multipolygon([Polygon(polygon.border,
                                 reverse_multiregion(polygon.holes))
                         for polygon in multipolygon.polygons])


def reverse_multipolygon_holes_contours(multipolygon: Multipolygon
                                        ) -> Multipolygon:
    return Multipolygon([Polygon(polygon.border,
                                 [reverse_region(hole)
                                  for hole in polygon.holes])
                         for polygon in multipolygon.polygons])


reverse_multiregion = reverse_sequence


def reverse_multiregion_coordinates(multiregion: Multiregion) -> Multiregion:
    return [reverse_region_coordinates(region) for region in multiregion]


def reverse_multiregion_regions(multiregion: Multiregion) -> Multiregion:
    return [reverse_region(region) for region in multiregion]


def reverse_multisegment(multisegment: Multisegment) -> Multisegment:
    return Multisegment(reverse_sequence(multisegment.segments))


def reverse_multisegment_coordinates(multisegment: Multisegment
                                     ) -> Multisegment:
    return Multisegment(reverse_segments_sequence_coordinates(
            multisegment.segments))


def reverse_multisegment_endpoints(multisegment: Multisegment) -> Multisegment:
    return Multisegment(reverse_segments_sequence_endpoints(
            multisegment.segments))


def reverse_point_coordinates(point: Point) -> Point:
    return Point(point.y, point.x)


def reverse_polygon_coordinates(polygon: Polygon) -> Polygon:
    return Polygon(reverse_contour_coordinates(polygon.border),
                   reverse_multiregion_coordinates(polygon.holes))


reverse_region = reverse_contour
reverse_region_coordinates = reverse_contour_coordinates


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)


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


def multipolygon_to_multiregion(multipolygon: Multipolygon) -> Multiregion:
    assert not any(polygon.holes for polygon in multipolygon.polygons)
    return [polygon.border for polygon in multipolygon.polygons]


def multiregion_to_multipolygon(multiregion: Multiregion) -> Multipolygon:
    return Multipolygon([Polygon(region, []) for region in multiregion])


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


def is_holeless_mix_empty(mix: HolelessMix) -> bool:
    multipoint, multisegment, multiregion = mix
    return not (multipoint.points or multisegment.segments
                or multiregion)


def is_mix_empty(mix: Mix) -> bool:
    multipoint, multisegment, multipolygon = mix
    return not (multipoint.points or multisegment.segments
                or multipolygon.polygons)


def to_multipolygon_contours(multipolygon: Multipolygon) -> Iterable[Contour]:
    for polygon in multipolygon.polygons:
        yield polygon.border
        yield from polygon.holes


def _to_counterclockwise_vertices(vertices: Sequence[Point]
                                  ) -> Sequence[Point]:
    if _to_first_angle_orientation(vertices) is not Orientation.CLOCKWISE:
        vertices = vertices[:1] + vertices[1:][::-1]
    return vertices


def _to_first_angle_orientation(vertices: Sequence[Point]) -> Orientation:
    return _context.angle_orientation(vertices[0], vertices[-1], vertices[1])
