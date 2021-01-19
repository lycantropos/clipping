from typing import (Callable,
                    Sequence,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Multipoint as _Multipoint,
                          Multisegment as _Multisegment,
                          Point as _Point,
                          Polygon as _Polygon)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
Multipolygon = Sequence[_Polygon]
LinearMix = Tuple[_Multipoint, _Multisegment]
Mix = Tuple[_Multipoint, _Multisegment, Multipolygon]
HolelessMix = Tuple[_Multipoint, _Multisegment, Multiregion]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
