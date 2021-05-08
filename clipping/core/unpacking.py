from typing import (Sequence,
                    Union)

from ground.base import Context
from ground.hints import (Contour,
                          Empty,
                          Linear,
                          Maybe,
                          Mix,
                          Multipoint,
                          Multipolygon,
                          Multisegment,
                          Point,
                          Polygon,
                          Segment,
                          Shaped)


def unpack_linear_mix(discrete: Maybe[Multipoint],
                      linear: Maybe[Linear],
                      context: Context
                      ) -> Union[Empty, Mix, Multipoint, Linear]:
    return (linear
            if discrete is context.empty
            else (discrete
                  if linear is context.empty
                  else context.mix_cls(discrete, linear, context.empty)))


def unpack_mix(discrete: Multipoint,
               linear: Linear,
               shaped: Maybe[Shaped],
               context: Context
               ) -> Union[Empty, Linear, Mix, Multipoint, Shaped]:
    empty = context.empty
    return ((shaped
             if linear is empty
             else (linear
                   if shaped is empty
                   else context.mix_cls(discrete, linear, shaped)))
            if discrete is empty
            else (discrete
                  if shaped is empty and linear is empty
                  else context.mix_cls(discrete, linear, shaped)))


def unpack_points(points: Sequence[Point], context: Context
                  ) -> Union[Empty, Multipoint]:
    return context.multipoint_cls(points) if points else context.empty


def unpack_polygons(polygons: Sequence[Polygon],
                    context: Context) -> Union[Empty, Multipolygon, Polygon]:
    return ((context.multipolygon_cls(polygons)
             if len(polygons) > 1
             else polygons[0])
            if polygons
            else context.empty)


def unpack_regions(regions: Sequence[Contour],
                   context: Context) -> Union[Empty, Polygon, Multipolygon]:
    polygon_cls = context.polygon_cls
    return ((context.multipolygon_cls([polygon_cls(region, [])
                                       for region in regions])
             if len(regions) > 1
             else polygon_cls(regions[0], []))
            if regions
            else context.empty)


def unpack_segments(segments: Sequence[Segment],
                    context: Context) -> Union[Empty, Multisegment, Segment]:
    return ((context.multisegment_cls(segments)
             if len(segments) > 1
             else segments[0])
            if segments
            else context.empty)
