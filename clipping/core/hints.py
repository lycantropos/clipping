from typing import (Callable,
                    List,
                    Tuple)

from ground.base import Orientation
from ground.hints import (Contour as _Contour,
                          Point as _Point,
                          Segment as _Segment)

Multipoint = List[_Point]
SegmentEndpoints = Tuple[_Point, _Point]
Multisegment = List[_Segment]
Region = _Contour
Multiregion = List[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = List[Polygon]
Mix = Tuple[Multipoint, Multisegment, Multipolygon]
HolelessMix = Tuple[Multipoint, Multisegment, Multiregion]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
