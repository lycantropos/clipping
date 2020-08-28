from numbers import Real
from typing import (List,
                    Tuple,
                    Type)

Coordinate = Real
Base = Type[Coordinate]
Point = Tuple[Coordinate, Coordinate]
Multipoint = List[Point]
Segment = Tuple[Point, Point]
Multisegment = List[Segment]
Contour = Region = List[Point]
Multiregion = List[Region]
Polygon = Tuple[Region, Multiregion]
Multipolygon = List[Polygon]
Mix = Tuple[Multipoint, Multisegment, Multipolygon]
HolelessMix = Tuple[Multipoint, Multisegment, Multiregion]
