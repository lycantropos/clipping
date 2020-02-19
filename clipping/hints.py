from numbers import Real
from typing import (List,
                    Tuple,
                    Type)

Coordinate = Real
Base = Type[Coordinate]
Point = Tuple[Coordinate, Coordinate]
BoundingBox = Tuple[Coordinate, Coordinate, Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = List[Point]
Polygon = Tuple[Contour, List[Contour]]
Multipolygon = List[Polygon]
