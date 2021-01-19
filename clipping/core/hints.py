from numbers import Real
from typing import (Callable,
                    List,
                    Tuple,
                    Type)

from ground.base import Orientation
from ground.hints import (Point as _Point,
                          Segment as _Segment)

Coordinate = Real
Base = Type[Coordinate]
Multipoint = List[_Point]
SegmentEndpoints = Tuple[_Point, _Point]
Multisegment = List[_Segment]
Contour = Region = List[_Point]
Multiregion = List[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = List[Polygon]
Mix = Tuple[Multipoint, Multisegment, Multipolygon]
HolelessMix = Tuple[Multipoint, Multisegment, Multiregion]
Orienteer = Callable[[_Point, _Point, _Point], Orientation]
