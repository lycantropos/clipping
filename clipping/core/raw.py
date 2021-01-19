from itertools import repeat
from typing import Tuple

from ground.base import Context
from ground.hints import Contour, Multipoint, Multipolygon, Multisegment, \
    Point, Polygon, Segment

from .hints import Multiregion


def from_multisegment(multisegment: Multisegment):
    return multisegment.segments


def from_contour(contour: Contour):
    return contour


from_region = from_contour


def from_multiregion(multiregion):
    return [from_region(region) for region in multiregion]


def from_polygon(polygon: Polygon):
    return from_contour(polygon.border), from_multiregion(polygon.holes)


def from_multipolygon(multipolygon: Multipolygon):
    return [from_polygon(polygon) for polygon in multipolygon.polygons]


def to_point(raw) -> Point:
    return raw


def to_segment(raw) -> Segment:
    return raw


def to_multisegment(raw) -> Multisegment:
    return raw


def to_contour(raw) -> Contour:
    return raw


def to_polygon(raw, context: Context) -> Polygon:
    raw_border, raw_holes = raw
    return context.polygon_cls(raw_border, raw_holes)


def to_multipolygon(raw, context: Context) -> Multipolygon:
    return context.multipolygon_cls(list(map(to_polygon, raw,
                                             repeat(context))))


def to_holeless_mix(raw) -> Tuple[Multipoint, Multisegment, Multiregion]:
    return raw


def to_mix(raw, context: Context
           ) -> Tuple[Multipoint, Multisegment, Multipolygon]:
    raw_multipoint, raw_multisegment, raw_multipolygon = raw
    return (raw_multipoint,
            to_multisegment(raw_multisegment),
            to_multipolygon(raw_multipolygon, context))
