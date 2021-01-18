from itertools import repeat
from typing import Sequence, Tuple

from ground.base import Context
from ground.hints import Contour, Multipoint, Multipolygon, Multisegment, \
    Point, Polygon, \
    Segment

from .hints import Multiregion


def from_point(point: Point):
    return point.x, point.y


def from_segment(segment: Segment):
    return from_point(segment.start), from_point(segment.end)


def from_multisegment(multisegment: Multisegment):
    return [from_segment(segment) for segment in multisegment.segments]


def from_segments(segments: Sequence[Segment]):
    return [from_segment(segment) for segment in segments]


def from_contour(contour: Contour):
    return [from_point(vertex) for vertex in contour.vertices]


from_region = from_contour


def from_multiregion(multiregion):
    return [from_region(region) for region in multiregion]


def from_polygon(polygon: Polygon):
    return from_contour(polygon.border), from_multiregion(polygon.holes)


def from_multipolygon(multipolygon: Multipolygon):
    return [from_polygon(polygon) for polygon in multipolygon.polygons]


def to_point(raw, context: Context) -> Point:
    return context.point_cls(*raw)


def to_segment(raw, context: Context) -> Segment:
    return context.segment_cls(*map(to_point, raw, repeat(context)))


def to_multisegment(raw, context: Context) -> Multisegment:
    return context.multisegment_cls(list(map(to_segment, raw,
                                             repeat(context))))


def to_contour(raw, context: Context) -> Contour:
    return context.contour_cls(*map(to_point, raw, repeat(context)))


def to_multiregion(raw, context: Context) -> Multiregion:
    return list(map(to_contour, raw,
                    repeat(context)))


def to_polygon(raw, context: Context) -> Polygon:
    raw_border, raw_holes = raw
    return context.polygon_cls(to_contour(raw_border, context,
                                          repeat(context)),
                               to_multiregion(raw_holes, context))


def to_multipolygon(raw, context: Context) -> Multipolygon:
    return context.multipolygon_cls(list(map(to_polygon, raw,
                                             repeat(context))))


def to_multipoint(raw, context: Context) -> Multipoint:
    return context.multipoint_cls(list(map(to_point, raw, repeat(context))))


def to_holeless_mix(raw, context: Context
                    ) -> Tuple[Multipoint, Multisegment, Multiregion]:
    raw_multipoint, raw_multisegment, raw_multiregion = raw
    return (to_multipoint(raw_multipoint, context),
            to_multisegment(raw_multisegment, context),
            to_multiregion(raw_multiregion, context))


def to_mix(raw, context: Context
           ) -> Tuple[Multipoint, Multisegment, Multipolygon]:
    raw_multipoint, raw_multisegment, raw_multipolygon = raw
    return (to_multipoint(raw_multipoint, context),
            to_multisegment(raw_multisegment, context),
            to_multipolygon(raw_multipolygon, context))
