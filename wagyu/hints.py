from numbers import Real
from typing import (List,
                    Tuple,
                    Type)

Coordinate = Real
Base = Type[Coordinate]
Point = Tuple[Coordinate, Coordinate]
Contour = List[Point]
Polygon = Tuple[Contour, List[Contour]]
Multipolygon = List[Polygon]
