from typing import (Callable,
                    List,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Multipoint as _Multipoint,
                          Point as _Point,
                          Segment as _Segment)

SegmentEndpoints = Tuple[_Point, _Point]
Multisegment = List[_Segment]
Region = _Contour
Multiregion = List[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = List[Polygon]
Mix = Tuple[_Multipoint, Multisegment, Multipolygon]
HolelessMix = Tuple[_Multipoint, Multisegment, Multiregion]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
