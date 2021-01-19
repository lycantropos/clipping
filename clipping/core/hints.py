from typing import (Callable,
                    Sequence,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Multipoint as _Multipoint,
                          Multipolygon as _Multipolygon,
                          Multisegment as _Multisegment,
                          Point as _Point)

SegmentEndpoints = Tuple[_Point, _Point]
Region = _Contour
Multiregion = Sequence[Region]
HolelessMix = Tuple[_Multipoint, _Multisegment, Multiregion]
LinearMix = Tuple[_Multipoint, _Multisegment]
Mix = Tuple[_Multipoint, _Multisegment, _Multipolygon]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
