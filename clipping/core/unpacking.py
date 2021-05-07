from typing import (Sequence,
                    Union)

from ground.base import Context
from ground.hints import (Empty,
                          Linear,
                          Maybe,
                          Mix,
                          Multipoint,
                          Multisegment,
                          Point,
                          Segment)


def unpack_points(points: Sequence[Point],
                  context: Context) -> Union[Empty, Multipoint]:
    return context.multipoint_cls(points) if points else context.empty


def unpack_segments(segments: Sequence[Segment],
                    context: Context) -> Union[Empty, Multisegment, Segment]:
    return ((context.multisegment_cls(segments)
             if len(segments) > 1
             else segments[0])
            if segments
            else context.empty)


def unpack_linear_mix(discrete: Maybe[Multipoint],
                      linear: Maybe[Linear],
                      context: Context
                      ) -> Union[Empty, Mix, Multipoint, Linear]:
    return (linear
            if discrete is context.empty
            else (discrete
                  if linear is context.empty
                  else context.mix_cls(discrete, linear, context.empty)))
