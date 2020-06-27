from numbers import Real
from typing import (List,
                    Tuple,
                    Type)

Coordinate = Real
Base = Type[Coordinate]
Point = Tuple[Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = List[Point]
Polygon = Tuple[Contour, List[Contour]]
Multipoint = List[Point]
Multipolygon = List[Polygon]
Multisegment = List[Segment]
Mix = Tuple[Multipoint, Multisegment, Multipolygon]
