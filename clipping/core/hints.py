from numbers import Real
from typing import (Callable,
                    List,
                    Tuple,
                    Type)

from ground.base import Orientation

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
Box = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]
Orienteer = Callable[[Point, Point, Point], Orientation]
