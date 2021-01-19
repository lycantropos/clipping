from typing import (Callable,
                    Sequence,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Multipoint as _Multipoint,
                          Multisegment as _Multisegment,
                          Point as _Point)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = Sequence[Polygon]
Mix = Tuple[_Multipoint, _Multisegment, Multipolygon]
HolelessMix = Tuple[_Multipoint, _Multisegment, Multiregion]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
